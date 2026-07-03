import fitz

from app.adapters.pdf.parser import extract_text_from_pdf
from app.domain.documents import extract_structured_fields


def _make_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_extract_text_from_pdf_reads_hotel_confirmation() -> None:
    payload = _make_pdf(
        "Hotel Confirmation\nCheck-in: Oct 10, 2026 at 3:00 PM\n"
        "Check-out: Oct 15, 2026 at 11:00 AM\nConfirmation code: HT-998877"
    )
    text = extract_text_from_pdf(payload)
    assert "Check-in" in text
    fields = extract_structured_fields(text)
    assert fields.check_in is not None
    assert "Oct 10" in fields.check_in
