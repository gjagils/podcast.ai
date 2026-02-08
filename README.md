# Podcast.ai - Audio Recap

Zet een Word-document om in een podcast van 5-10 minuten. Twee presentatoren
(Emma en Lucas) bespreken de inhoud op een toegankelijke, conversationele manier
-- vergelijkbaar met de Audio Recap functie van StudyFetch.

## Wat doet het?

1. **Upload** je Word-document (.docx) via de website
2. **Kies** de gewenste duur (5-10 minuten)
3. **AI genereert** een podcast-script waarin alle stof wordt uitgelegd
4. **Luister** direct in de browser of download de MP3

## Draaien op Synology (Docker / Portainer)

### Voorbereiding op je Synology

SSH naar je Synology en maak de projectmap aan:

```bash
# Maak de map aan (pas het pad aan naar jouw situatie)
mkdir -p /volume1/docker/podcast-ai/output

# Clone de repository
cd /volume1/docker/podcast-ai
git clone https://github.com/gjagils/podcast.ai.git .

# OF kopieer de bestanden handmatig naar /volume1/docker/podcast-ai/
```

### Optie 1: Portainer Stack (aanbevolen)

1. Open **Portainer** in je browser
2. Ga naar **Stacks** > **Add stack**
3. Geef de stack een naam: `podcast-ai`
4. Plak de volgende **docker-compose** configuratie:

```yaml
version: "3.8"

services:
  podcast-ai:
    build: /volume1/docker/podcast-ai
    container_name: podcast-ai
    restart: unless-stopped
    ports:
      - "8100:8000"
    environment:
      - OPENAI_API_KEY=sk-jouw-api-key-hier
    volumes:
      - /volume1/docker/podcast-ai/output:/app/output
```

5. Vul bij `OPENAI_API_KEY` je echte API-key in
6. Klik op **Deploy the stack**
7. Ga naar `http://SYNOLOGY-IP:8100` in je browser

### Optie 2: Docker Compose via SSH

```bash
cd /volume1/docker/podcast-ai

# Maak een .env bestand
echo "OPENAI_API_KEY=sk-jouw-api-key-hier" > .env

# Build en start
docker-compose up -d --build

# Logs bekijken
docker-compose logs -f
```

### Na installatie

- De website is bereikbaar op: `http://SYNOLOGY-IP:8100`
- Gegenereerde podcasts staan in: `/volume1/docker/podcast-ai/output/`
- Poort wijzigen? Pas `8100:8000` aan (het eerste getal is de externe poort)

---

## Lokaal draaien (zonder Docker)

### Installatie

```bash
git clone <repo-url>
cd podcast.ai

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# ffmpeg is nodig
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # Mac
```

### Configuratie

```bash
cp .env.example .env
# Vul je OpenAI API-key in
```

### Web interface starten

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in je browser.

### Command-line gebruik

```bash
python main.py document.docx              # Standaard 7 minuten
python main.py document.docx --duur 10    # 10 minuten
python main.py document.docx --alleen-script  # Alleen script
```

## Projectstructuur

```
podcast.ai/
├── app.py                   # Web applicatie (FastAPI)
├── main.py                  # CLI versie
├── Dockerfile               # Docker image
├── docker-compose.yml       # Docker Compose config
├── requirements.txt         # Python packages
├── .env.example             # Voorbeeld configuratie
├── static/
│   ├── index.html           # Website
│   ├── style.css            # Styling
│   └── app.js               # Frontend logica
├── src/
│   ├── document_reader.py   # Leest Word-documenten
│   ├── script_generator.py  # Genereert podcast-script met AI
│   └── audio_generator.py   # Maakt audio met Nederlandse stemmen
└── output/                  # Hier komen de podcasts
```

## Stemmen

De podcast gebruikt twee Nederlandse stemmen:
- **Emma** (Fenna) - Vrouwelijke stem, leidt het gesprek
- **Lucas** (Maarten) - Mannelijke stem, geeft uitleg

## Vereisten

- OpenAI API-key
- Docker (voor Synology) of Python 3.10+ (lokaal)
- Internetverbinding (voor AI en text-to-speech)
