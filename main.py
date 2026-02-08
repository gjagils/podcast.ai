"""
Podcast.ai - Audio Recap Generator

Zet een Word-document om in een podcast van 5-10 minuten
waarin de inhoud op een toegankelijke manier wordt uitgelegd.

Gebruik:
    python main.py document.docx
    python main.py document.docx --duur 10
    python main.py document.docx --output mijn_podcast.mp3
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.document_reader import read_docx
from src.script_generator import generate_script
from src.audio_generator import generate_audio


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Podcast.ai - Zet een Word-document om in een podcast",
    )
    parser.add_argument(
        "document",
        help="Pad naar het Word-document (.docx)",
    )
    parser.add_argument(
        "--duur",
        type=int,
        default=7,
        choices=range(5, 11),
        metavar="5-10",
        help="Gewenste duur van de podcast in minuten (standaard: 7)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Pad voor het output MP3-bestand (standaard: output/<documentnaam>.mp3)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model voor scriptgeneratie (standaard: gpt-4o)",
    )
    parser.add_argument(
        "--alleen-script",
        action="store_true",
        help="Genereer alleen het script, geen audio",
    )

    args = parser.parse_args()

    # Stap 1: Document inlezen
    print(f"📄 Document inlezen: {args.document}")
    try:
        document = read_docx(args.document)
    except (FileNotFoundError, ValueError) as e:
        print(f"Fout: {e}")
        sys.exit(1)

    print(f"   Titel: {document['title']}")
    print(f"   Secties: {len(document['sections'])}")
    total_words = len(document["full_text"].split())
    print(f"   Woorden: {total_words}")

    # Stap 2: Podcast-script genereren
    print(f"\n🎙️  Podcast-script genereren ({args.duur} minuten)...")
    try:
        script = generate_script(
            document,
            duration_minutes=args.duur,
            model=args.model,
        )
    except Exception as e:
        print(f"Fout bij scriptgeneratie: {e}")
        sys.exit(1)

    print(f"   Script: {len(script)} segmenten gegenereerd")

    # Script tonen als --alleen-script is meegegeven
    if args.alleen_script:
        print("\n--- PODCAST SCRIPT ---\n")
        for segment in script:
            print(f"{segment['speaker']}: {segment['text']}\n")
        return

    # Script ook opslaan als tekstbestand
    doc_name = Path(args.document).stem
    script_path = Path("output") / f"{doc_name}_script.txt"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    with open(script_path, "w", encoding="utf-8") as f:
        for segment in script:
            f.write(f"{segment['speaker']}: {segment['text']}\n\n")
    print(f"   Script opgeslagen: {script_path}")

    # Stap 3: Audio genereren
    output_path = args.output or str(Path("output") / f"{doc_name}.mp3")
    print(f"\n🔊 Audio genereren...")
    try:
        result_path = generate_audio(script, output_path)
    except Exception as e:
        print(f"Fout bij audiogeneratie: {e}")
        sys.exit(1)

    print(f"\n✅ Podcast klaar! Bestand: {result_path}")


if __name__ == "__main__":
    main()
