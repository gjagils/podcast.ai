"""Reads Word documents and extracts structured text content."""

from pathlib import Path
from docx import Document


def read_docx(file_path: str) -> dict:
    """Read a .docx file and extract text with structure.

    Returns a dict with:
        - title: document title (first heading or filename)
        - sections: list of {heading, content} dicts
        - full_text: all text concatenated
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")
    if path.suffix.lower() != ".docx":
        raise ValueError(f"Alleen .docx bestanden worden ondersteund, niet {path.suffix}")

    doc = Document(file_path)

    sections = []
    current_heading = None
    current_content = []
    title = path.stem

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if para.style.name.startswith("Heading"):
            # Save previous section
            if current_heading or current_content:
                sections.append({
                    "heading": current_heading or "",
                    "content": "\n".join(current_content),
                })
            # First heading becomes the title
            if not sections and current_heading is None and not current_content:
                title = text
            current_heading = text
            current_content = []
        else:
            current_content.append(text)

    # Save last section
    if current_heading or current_content:
        sections.append({
            "heading": current_heading or "",
            "content": "\n".join(current_content),
        })

    full_text = "\n\n".join(
        (f"## {s['heading']}\n{s['content']}" if s["heading"] else s["content"])
        for s in sections
    )

    return {
        "title": title,
        "sections": sections,
        "full_text": full_text,
    }
