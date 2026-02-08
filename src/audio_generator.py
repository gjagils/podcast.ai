"""Genereert audio van het podcast-script met Nederlandse stemmen via edge-tts."""

import asyncio
import tempfile
from pathlib import Path

import edge_tts
from pydub import AudioSegment

# Nederlandse stemmen via Edge TTS
VOICES = {
    "Emma": "nl-NL-FennaNeural",    # Vrouwelijke Nederlandse stem
    "Lucas": "nl-NL-MaartenNeural",  # Mannelijke Nederlandse stem
}

SPEECH_RATE = "+0%"
PAUSE_BETWEEN_SPEAKERS_MS = 600


async def _generate_segment(text: str, voice: str, output_path: str) -> None:
    """Genereer een audio-segment voor een stuk tekst."""
    communicate = edge_tts.Communicate(text, voice, rate=SPEECH_RATE)
    await communicate.save(output_path)


async def _generate_all_segments(
    script: list[dict], temp_dir: str
) -> list[str]:
    """Genereer alle audio-segmenten van het script."""
    tasks = []
    paths = []

    for i, segment in enumerate(script):
        voice = VOICES.get(segment["speaker"], VOICES["Emma"])
        path = str(Path(temp_dir) / f"segment_{i:04d}.mp3")
        paths.append(path)
        tasks.append(_generate_segment(segment["text"], voice, path))

    # Verwerk in batches van 5 om de API niet te overbelasten
    batch_size = 5
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i : i + batch_size]
        await asyncio.gather(*batch)

    return paths


def generate_audio(script: list[dict], output_path: str) -> str:
    """Genereer de volledige podcast-audio van een script.

    Args:
        script: Lijst van {'speaker': str, 'text': str} dicts.
        output_path: Pad waar het MP3-bestand wordt opgeslagen.

    Returns:
        Het pad naar het gegenereerde MP3-bestand.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Genereer alle segmenten
        segment_paths = asyncio.run(
            _generate_all_segments(script, temp_dir)
        )

        # Combineer alle segmenten tot een podcast
        pause = AudioSegment.silent(duration=PAUSE_BETWEEN_SPEAKERS_MS)
        podcast = AudioSegment.empty()

        for path in segment_paths:
            segment_audio = AudioSegment.from_mp3(path)
            if len(podcast) > 0:
                podcast += pause
            podcast += segment_audio

        # Exporteer als MP3
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        podcast.export(str(output), format="mp3")

    return str(output)
