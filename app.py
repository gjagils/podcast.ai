"""
Podcast.ai - Web applicatie

FastAPI backend voor de Audio Recap generator.
Host dit op je Synology NAS via Docker.
"""

import shutil
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.document_reader import read_docx
from src.script_generator import generate_script
from src.audio_generator import generate_audio

load_dotenv()

app = FastAPI(title="Podcast.ai - Audio Recap")

# Mappen aanmaken
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Static files
STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

# Actieve taken bijhouden
jobs: dict[str, dict] = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload een Word-document en geef info terug."""
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Alleen .docx bestanden zijn toegestaan.")

    job_id = uuid.uuid4().hex[:12]
    file_path = UPLOAD_DIR / f"{job_id}.docx"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        document = read_docx(str(file_path))
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(400, f"Kan document niet lezen: {e}")

    word_count = len(document["full_text"].split())

    jobs[job_id] = {
        "status": "uploaded",
        "file_path": str(file_path),
        "filename": file.filename,
        "document": document,
    }

    return {
        "job_id": job_id,
        "title": document["title"],
        "sections": len(document["sections"]),
        "words": word_count,
    }


@app.post("/api/generate/{job_id}")
def generate_podcast(
    job_id: str,
    duration: int = Form(default=7),
    model: str = Form(default="gpt-4o"),
):
    """Genereer de podcast voor een geupload document."""
    if job_id not in jobs:
        raise HTTPException(404, "Upload niet gevonden.")

    job = jobs[job_id]
    if job["status"] == "processing":
        raise HTTPException(409, "Podcast wordt al gegenereerd.")

    job["status"] = "processing"
    duration = max(5, min(10, duration))

    try:
        # Script genereren
        job["step"] = "script"
        script = generate_script(
            job["document"],
            duration_minutes=duration,
            model=model,
        )

        # Script opslaan
        script_path = OUTPUT_DIR / f"{job_id}_script.txt"
        with open(script_path, "w", encoding="utf-8") as f:
            for segment in script:
                f.write(f"{segment['speaker']}: {segment['text']}\n\n")

        # Audio genereren
        job["step"] = "audio"
        audio_path = str(OUTPUT_DIR / f"{job_id}.mp3")
        generate_audio(script, audio_path)

        job["status"] = "done"
        job["audio_file"] = f"{job_id}.mp3"
        job["script_file"] = f"{job_id}_script.txt"

        # Upload verwijderen
        Path(job["file_path"]).unlink(missing_ok=True)

        return {
            "status": "done",
            "audio_url": f"/output/{job_id}.mp3",
            "script_url": f"/output/{job_id}_script.txt",
        }

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        raise HTTPException(500, f"Fout bij generatie: {e}")


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Haal de status op van een taak."""
    if job_id not in jobs:
        raise HTTPException(404, "Taak niet gevonden.")

    job = jobs[job_id]
    result = {"status": job["status"]}

    if job["status"] == "processing":
        result["step"] = job.get("step", "")
    elif job["status"] == "done":
        result["audio_url"] = f"/output/{job['audio_file']}"
        result["script_url"] = f"/output/{job['script_file']}"
    elif job["status"] == "error":
        result["error"] = job.get("error", "Onbekende fout")

    return result


@app.get("/api/download/{job_id}")
async def download_audio(job_id: str):
    """Download het MP3-bestand."""
    if job_id not in jobs or jobs[job_id]["status"] != "done":
        raise HTTPException(404, "Podcast niet gevonden.")

    audio_path = OUTPUT_DIR / jobs[job_id]["audio_file"]
    original_name = Path(jobs[job_id]["filename"]).stem
    return FileResponse(
        str(audio_path),
        media_type="audio/mpeg",
        filename=f"{original_name}_podcast.mp3",
    )
