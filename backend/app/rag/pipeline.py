"""Full RAG pipeline orchestrator — document ingestion to vector store."""
from app.core.pdf_parser import extract_text_from_pdf, extract_text_from_string
from app.core.chunker import chunk_document
from app.core.vector_store import index_chunks
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def ingest_document(
    document_id: str,
    file_bytes: bytes | None = None,
    raw_text: str | None = None,
) -> tuple[str, int, int]:
    """
    Full document ingestion pipeline.

    Steps:
    1. Extract text from PDF bytes OR accept raw text.
    2. Chunk the text into semantic sections.
    3. Embed chunks and store in ChromaDB.

    Args:
        document_id: Unique document identifier.
        file_bytes:  PDF binary content (mutually exclusive with raw_text).
        raw_text:    Plain text content (mutually exclusive with file_bytes).

    Returns:
        Tuple of (full_text, page_count, chunk_count).
    """
    if file_bytes:
        full_text, page_count = extract_text_from_pdf(file_bytes)
    elif raw_text:
        full_text, page_count = extract_text_from_string(raw_text)
    else:
        raise ValueError("Either file_bytes or raw_text must be provided.")

    word_count = len(full_text.split())
    logger.info("ingestion_started", document_id=document_id, word_count=word_count)

    chunks = chunk_document(document_id=document_id, text=full_text)
    index_chunks(chunks)

    logger.info(
        "ingestion_complete",
        document_id=document_id,
        page_count=page_count,
        chunk_count=len(chunks),
        word_count=word_count,
    )
    return full_text, page_count, len(chunks)
