"""Genereert audio van het podcast-script via OpenAI TTS of Edge TTS."""

import asyncio
import tempfile
from pathlib import Path

from openai import OpenAI
from pydub import AudioSegment

# --- OpenAI TTS stemmen ---
OPENAI_VOICES = {
    "Emma": "nova",
    "Lucas": "onyx",
    "Verteller": "nova",
}

# --- Edge TTS stemmen (gratis fallback) ---
EDGE_VOICES = {
    "Emma": "nl-NL-FennaNeural",
    "Lucas": "nl-NL-MaartenNeural",
    "Verteller": "nl-NL-ColetteNeural",
}

EDGE_SPEECH_RATE = "+15%"
PAUSE_BETWEEN_SPEAKERS_MS = 400


# === OpenAI TTS ===

def _generate_segment_openai(text: str, voice: str, output_path: str) -> None:
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text,
        speed=1.1,
    )
    response.stream_to_file(output_path)


def _generate_audio_openai(script: list[dict], output_path: str) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        paths = []
        for i, segment in enumerate(script):
            voice = OPENAI_VOICES.get(segment["speaker"], OPENAI_VOICES["Emma"])
            path = str(Path(temp_dir) / f"segment_{i:04d}.mp3")
            _generate_segment_openai(segment["text"], voice, path)
            paths.append(path)

        return _combine_segments(paths, output_path)


# === Edge TTS (gratis fallback) ===

async def _generate_segment_edge(text: str, voice: str, output_path: str) -> None:
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=EDGE_SPEECH_RATE)
    await communicate.save(output_path)


async def _generate_all_segments_edge(script: list[dict], temp_dir: str) -> list[str]:
    paths = []
    tasks = []

    for i, segment in enumerate(script):
        voice = EDGE_VOICES.get(segment["speaker"], EDGE_VOICES["Emma"])
        path = str(Path(temp_dir) / f"segment_{i:04d}.mp3")
        paths.append(path)
        tasks.append(_generate_segment_edge(segment["text"], voice, path))

    batch_size = 5
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i : i + batch_size]
        await asyncio.gather(*batch)

    return paths


def _generate_audio_edge(script: list[dict], output_path: str) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        paths = asyncio.run(_generate_all_segments_edge(script, temp_dir))
        return _combine_segments(paths, output_path)


# === Gedeeld ===

def _combine_segments(paths: list[str], output_path: str) -> str:
    pause = AudioSegment.silent(duration=PAUSE_BETWEEN_SPEAKERS_MS)
    podcast = AudioSegment.empty()

    for path in paths:
        segment_audio = AudioSegment.from_mp3(path)
        if len(podcast) > 0:
            podcast += pause
        podcast += segment_audio

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    podcast.export(str(output), format="mp3")
    return str(output)


def generate_audio(script: list[dict], output_path: str, tts_engine: str = "openai") -> str:
    """Genereer podcast-audio.

    Args:
        script: Lijst van {'speaker': str, 'text': str} dicts.
        output_path: Pad voor het MP3-bestand.
        tts_engine: "openai" (natuurlijk, ~$0.10/podcast) of "edge" (gratis).
    """
    if tts_engine == "openai":
        return _generate_audio_openai(script, output_path)
    else:
        return _generate_audio_edge(script, output_path)
