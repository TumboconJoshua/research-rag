from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from pydantic import BaseModel
from app.config import get_settings
from app.rag.pipeline import ingest_document
from app.utils.logger import get_logger
from app.utils.convex_client import get_convex_client
from app.utils.rate_limiter import limiter

logger = get_logger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    word_count: int
    chunk_count: int
    status: str


@router.post("/upload-document", response_model=UploadResponse)
@limiter.limit("5/minute")
async def upload_document(
    request: Request,
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
):
    """
    Accept a PDF file upload or raw text paste and ingest it into the RAG system.
    Generates a unique document_id in Convex, extracts text, chunks, embeds, and stores.
    """
    settings = get_settings()

    if file is None and not text:
        raise HTTPException(status_code=400, detail="Either a PDF file or raw text must be provided.")

    # Validate file size
    if file:
        file_bytes = await file.read()
        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the {settings.max_upload_size_mb} MB limit.",
            )
        if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
            raise HTTPException(status_code=415, detail="Only PDF files are accepted.")
    else:
        file_bytes = None

    filename = file.filename if file else "pasted_text.txt"
    convex = get_convex_client()

    try:
        # 1. Create document entry in Convex
        word_est = len(text.split()) if text else 0
        convex_doc_id = convex.mutation(
            "documents:createDocument",
            {
                "filename": filename,
                "fileType": "pdf" if file else "text",
                "wordCount": word_est,
            }
        )
        document_id = str(convex_doc_id)

        # 2. Run ingestion pipeline (text extraction, chunking, embedding)
        logger.info("ingestion_pipeline_started", document_id=document_id)
        full_text, page_count, chunk_count = await ingest_document(
            document_id=document_id,
            file_bytes=file_bytes,
            raw_text=text,
        )
        word_count = len(full_text.split())
        logger.info("ingestion_pipeline_finished", document_id=document_id, chunk_count=chunk_count)

        # 3. Update status in Convex
        logger.info("updating_convex_status", id=document_id)
        convex.mutation(
            "documents:updateDocumentStatus", 
            {"id": convex_doc_id, "status": "ready"}
        )
        logger.info("upload_complete", document_id=document_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        import traceback
        error_details = traceback.format_exc()
        logger.error("upload_failed", error=str(exc), traceback=error_details)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(exc)}") from exc

    logger.info("document_uploaded", document_id=document_id, filename=filename)
    return UploadResponse(
        document_id=document_id,
        filename=filename,
        page_count=page_count,
        word_count=word_count,
        chunk_count=chunk_count,
        status="ready",
    )
