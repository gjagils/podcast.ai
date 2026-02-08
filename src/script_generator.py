"""Generates a conversational podcast script from document content using OpenAI."""

from openai import OpenAI

SYSTEM_PROMPT = """\
Je bent een podcast-scriptschrijver. Je schrijft scripts voor een educatieve \
podcast met twee presentatoren: Emma en Lucas. De podcast heet "Audio Recap".

Regels:
- Schrijf een natuurlijk, conversationeel script in het Nederlands.
- Emma leidt het gesprek en stelt vragen. Lucas geeft uitleg en vult aan.
- Leg ALLE belangrijke concepten uit het bronmateriaal uit op een toegankelijke manier.
- Gebruik voorbeelden en analogieen om moeilijke stof begrijpelijk te maken.
- Het script moet resulteren in een podcast van {duration} minuten wanneer voorgelezen.
- Reken op circa 150 woorden per minuut gesproken tekst.
- Het script moet dus ongeveer {word_count} woorden bevatten.
- Begin met een korte intro waarin Emma het onderwerp introduceert.
- Eindig met een samenvatting van de belangrijkste punten.
- Gebruik GEEN aanwijzingen als [lacht], [pauze] etc. Alleen gesproken tekst.
- Formaat: elke regel begint met "Emma:" of "Lucas:" gevolgd door hun tekst.
- Zorg dat het script vloeiend en natuurlijk klinkt, alsof twee mensen echt met \
elkaar praten.
- Sla NIETS over uit het bronmateriaal. Alles moet aan bod komen.
"""

USER_PROMPT = """\
Schrijf een podcast-script op basis van het volgende document.

Documenttitel: {title}

Inhoud:
{content}

Schrijf het volledige script. Zorg dat alle informatie uit het document wordt behandeld \
in een podcast van {duration} minuten ({word_count} woorden).
"""


def generate_script(
    document: dict,
    duration_minutes: int = 7,
    api_key: str | None = None,
    model: str = "gpt-4o",
) -> list[dict]:
    """Generate a podcast script from document content.

    Args:
        document: Output from document_reader.read_docx()
        duration_minutes: Target duration in minutes (5-10)
        api_key: OpenAI API key (uses env var if None)
        model: OpenAI model to use

    Returns:
        List of dicts with 'speaker' and 'text' keys.
    """
    duration_minutes = max(5, min(10, duration_minutes))
    word_count = duration_minutes * 150

    client = OpenAI(api_key=api_key) if api_key else OpenAI()

    system = SYSTEM_PROMPT.format(duration=duration_minutes, word_count=word_count)
    user = USER_PROMPT.format(
        title=document["title"],
        content=document["full_text"],
        duration=duration_minutes,
        word_count=word_count,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        max_tokens=16000,
    )

    raw_script = response.choices[0].message.content
    return parse_script(raw_script)


def parse_script(raw_script: str) -> list[dict]:
    """Parse raw script text into structured segments.

    Returns list of {'speaker': 'Emma'|'Lucas', 'text': '...'} dicts.
    """
    lines = []
    current_speaker = None
    current_text = []

    for line in raw_script.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith("Emma:"):
            if current_speaker:
                lines.append({"speaker": current_speaker, "text": " ".join(current_text)})
            current_speaker = "Emma"
            current_text = [line[len("Emma:"):].strip()]
        elif line.startswith("Lucas:"):
            if current_speaker:
                lines.append({"speaker": current_speaker, "text": " ".join(current_text)})
            current_speaker = "Lucas"
            current_text = [line[len("Lucas:"):].strip()]
        else:
            current_text.append(line)

    if current_speaker:
        lines.append({"speaker": current_speaker, "text": " ".join(current_text)})

    return lines
