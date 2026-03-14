"""PDF text extraction using PyMuPDF."""
import io
import fitz  # PyMuPDF
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    """
    Extract all text from a PDF file.

    Args:
        file_bytes: Raw PDF binary content.

    Returns:
        Tuple of (full_text, page_count).
    """
    try:
        doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        page_count = len(doc)
        pages: list[str] = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                pages.append(f"[PAGE {page_num + 1}]\n{text}")

        full_text = "\n\n".join(pages)
        doc.close()

        logger.info("pdf_extracted", page_count=page_count, char_count=len(full_text))
        return full_text, page_count

    except Exception as exc:
        logger.error("pdf_extraction_failed", error=str(exc))
        raise ValueError(f"Failed to extract PDF text: {exc}") from exc


def extract_text_from_string(text: str) -> tuple[str, int]:
    """Pass-through for plain text input."""
    return text, 1
