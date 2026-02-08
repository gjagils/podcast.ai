# Podcast.ai - Audio Recap

Zet een Word-document om in een podcast van 5-10 minuten. Twee presentatoren
(Emma en Lucas) bespreken de inhoud op een toegankelijke, conversationele manier
-- vergelijkbaar met de Audio Recap functie van StudyFetch.

## Wat doet het?

1. **Leest** je Word-document (.docx) in
2. **Genereert** een podcast-script met AI (OpenAI) waarin alle stof wordt uitgelegd
3. **Maakt** een MP3-bestand met Nederlandse stemmen

## Installatie

```bash
# Clone de repository
git clone <repo-url>
cd podcast.ai

# Maak een virtuele omgeving aan
python -m venv venv
source venv/bin/activate  # Linux/Mac
# of: venv\Scripts\activate  # Windows

# Installeer de vereisten
pip install -r requirements.txt

# ffmpeg is nodig voor audiobewerking
# Ubuntu/Debian:
sudo apt install ffmpeg
# Mac:
brew install ffmpeg
```

## Configuratie

Maak een `.env` bestand aan op basis van het voorbeeld:

```bash
cp .env.example .env
```

Vul je OpenAI API-key in:

```
OPENAI_API_KEY=sk-jouw-api-key
```

## Gebruik

### Simpel

```bash
python main.py jouw_document.docx
```

Dit genereert een podcast van ~7 minuten en slaat het op als `output/jouw_document.mp3`.

### Opties

```bash
# Podcast van 10 minuten
python main.py document.docx --duur 10

# Eigen output-bestand
python main.py document.docx --output mijn_podcast.mp3

# Alleen het script genereren (geen audio)
python main.py document.docx --alleen-script

# Ander AI-model gebruiken
python main.py document.docx --model gpt-4o-mini
```

### Stap voor stap

1. Zet je Word-bestand in de `input/` map (optioneel, je kunt elk pad gebruiken)
2. Voer het commando uit: `python main.py input/mijn_bestand.docx`
3. Wacht tot het script en de audio zijn gegenereerd
4. Je podcast staat in de `output/` map

## Projectstructuur

```
podcast.ai/
├── main.py                  # Hoofdscript - start hier
├── requirements.txt         # Python packages
├── .env.example             # Voorbeeld configuratie
├── src/
│   ├── document_reader.py   # Leest Word-documenten
│   ├── script_generator.py  # Genereert podcast-script met AI
│   └── audio_generator.py   # Maakt audio met Nederlandse stemmen
├── input/                   # Plaats hier je Word-bestanden
└── output/                  # Hier komen de podcasts
```

## Stemmen

De podcast gebruikt twee Nederlandse stemmen:
- **Emma** (Fenna) - Vrouwelijke stem, leidt het gesprek
- **Lucas** (Maarten) - Mannelijke stem, geeft uitleg

## Vereisten

- Python 3.10+
- OpenAI API-key
- ffmpeg (voor audiobewerking)
- Internetverbinding (voor AI en text-to-speech)
