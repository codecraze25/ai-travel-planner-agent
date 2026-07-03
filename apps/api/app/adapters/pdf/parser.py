from __future__ import annotations

import fitz  # PyMuPDF


def extract_text_from_pdf(data: bytes) -> str:
    """Extract plain text from a PDF byte payload."""
    parts: list[str] = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            parts.append(page.get_text("text"))
    return "\n".join(parts).strip()
