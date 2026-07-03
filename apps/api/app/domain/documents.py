from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum

MAX_PDF_BYTES = 20 * 1024 * 1024
ALLOWED_MIME_TYPES = {"application/pdf"}


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    READY = "ready"
    FAILED = "failed"


@dataclass
class ExtractedFields:
    dates: list[str] = field(default_factory=list)
    times: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    reservation_numbers: list[str] = field(default_factory=list)
    passenger_names: list[str] = field(default_factory=list)
    confirmation_codes: list[str] = field(default_factory=list)
    check_in: str | None = None
    check_out: str | None = None
    policy_rules: list[str] = field(default_factory=list)


# Patterns that look like prompt-injection attempts in uploaded PDFs
_INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?)\b"),
    re.compile(r"(?i)\bdisregard\s+(all\s+)?(previous|prior|system)\b"),
    re.compile(r"(?i)\byou\s+are\s+now\b"),
    re.compile(r"(?i)\bsystem\s*:\s*"),
    re.compile(r"(?i)\bsend\s+(an?\s+)?email\s+to\b"),
    re.compile(r"(?i)\bbook\s+(the\s+)?hotel\b"),
]


def validate_upload(filename: str, content_type: str | None, size_bytes: int) -> None:
    if size_bytes <= 0:
        raise ValueError("Empty file is not allowed.")
    if size_bytes > MAX_PDF_BYTES:
        raise ValueError(f"File exceeds maximum size of {MAX_PDF_BYTES // (1024 * 1024)} MB.")
    lower = filename.lower()
    if not lower.endswith(".pdf"):
        raise ValueError("Only PDF files are allowed.")
    if (
        content_type
        and content_type not in ALLOWED_MIME_TYPES
        and content_type != "application/octet-stream"
    ):
        raise ValueError("Only PDF content type is allowed.")


def sanitize_document_text(text: str) -> str:
    """Treat PDF text as untrusted data; neutralize instruction-like phrases."""
    sanitized = text
    for pattern in _INJECTION_PATTERNS:
        sanitized = pattern.sub("[redacted-instruction]", sanitized)
    return sanitized


def contains_injection_attempt(text: str) -> bool:
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)


def extract_structured_fields(text: str) -> ExtractedFields:
    """Heuristic extraction of travel facts from PDF text (no LLM required)."""
    fields = ExtractedFields()

    # Dates: Oct 10, 2026 / 2026-10-10 / 10/10/2026
    date_patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ]
    dates: list[str] = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    fields.dates = _unique(dates)

    times = re.findall(r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b", text)
    fields.times = _unique(times)

    conf = re.findall(
        r"(?i)(?:confirmation|confirmation\s*(?:code|number)|conf(?:irmation)?\.?\s*#?|reservation\s*(?:number|#))\s*[:#]?\s*([A-Z0-9-]{5,20})",
        text,
    )
    fields.confirmation_codes = _unique(conf)
    fields.reservation_numbers = list(fields.confirmation_codes)

    check_in = re.search(
        r"(?i)check[-\s]?in\s*(?:date|on)?\s*[:\-]?\s*"
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?"
        r"|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})",
        text,
    )
    if check_in:
        fields.check_in = check_in.group(1)

    check_out = re.search(
        r"(?i)check[-\s]?out\s*(?:date|on)?\s*[:\-]?\s*"
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?"
        r"|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})",
        text,
    )
    if check_out:
        fields.check_out = check_out.group(1)

    # Optional time after check-in
    check_in_time = re.search(
        r"(?i)check[-\s]?in[^\n]{0,40}?(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
        text,
    )
    if check_in_time and check_in_time.group(1) not in fields.times:
        fields.times.insert(0, check_in_time.group(1))

    names = re.findall(
        r"(?i)(?:guest|passenger|traveler)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", text
    )
    fields.passenger_names = _unique(names)

    locations = re.findall(
        r"(?i)(?:hotel|property|location|address)\s*[:\-]?\s*([A-Za-z0-9 ,.'-]{3,60})",
        text,
    )
    fields.locations = _unique(locations)

    policy = re.findall(r"(?i)((?:cancellation|refund|non-refundable)[^\n.]{0,80})", text)
    fields.policy_rules = _unique(policy)

    return fields


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    text = text.strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip()
        if key and key.lower() not in seen:
            seen.add(key.lower())
            out.append(key)
    return out
