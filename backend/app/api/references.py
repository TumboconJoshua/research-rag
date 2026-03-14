from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.references.extractor import extract_references
from app.references.validator import validate_references
from app.references.schemas import ValidationReport
from app.core.vector_store import search_chunks
from app.utils.logger import get_logger
from app.utils.convex_client import get_convex_client
from app.utils.rate_limiter import limiter

logger = get_logger(__name__)
router = APIRouter()


class ValidateRequest(BaseModel):
    document_id: str
    raw_text: str | None = None  # Optional: pass text directly; else retrieve from vector store


@router.post("/validate-references", response_model=ValidationReport)
@limiter.limit("5/minute")
async def validate_references_endpoint(request: Request, body: ValidateRequest):
    """
    Extract all references from a document and validate them against
    Crossref, Semantic Scholar, and OpenAlex APIs.
    """
    document_id = body.document_id

    # Get document text — either passed directly or reconstructed from chunks
    if body.raw_text:
        text = body.raw_text
    else:
        # Retrieve reference-section chunks from vector store
        chunks = search_chunks(
            document_id=document_id,
            query="references bibliography citations",
            top_k=20,
        )
        if not chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for document {document_id}. Was it uploaded?",
            )
        # For reference extraction, use the raw text from all retrieved chunks
        # We need the original full text; pass it via raw_text field for best results
        text = "\n\n".join(c["text"] for c in chunks)

    try:
        logger.info("extracting_references_started", document_id=document_id)
        parsed_refs = extract_references(text)
        if not parsed_refs:
            logger.warning("no_references_extracted", document_id=document_id)
            raise HTTPException(
                status_code=422,
                detail="No references could be extracted from the document. Ensure it contains a References section.",
            )

        logger.info("validating_references_started", document_id=document_id, count=len(parsed_refs))
        report = await validate_references(
            document_id=document_id,
            parsed_refs=parsed_refs,
        )

        # Initialize Convex client
        convex = get_convex_client()

        # Save each validated reference to Convex
        logger.info("saving_references_to_convex", document_id=document_id)
        for ref in report.references:
            try:
                convex.mutation(
                    "documents:saveReference",
                    {
                        "documentId": document_id,
                        "index": ref.index,
                        "rawText": ref.raw_text,
                        "title": ref.title,
                        "authors": ref.authors,
                        "year": str(ref.year) if ref.year else None,
                        "journal": ref.journal,
                        "doi": ref.doi,
                        "status": ref.status.value,
                        "confidenceScore": ref.confidence_score,
                        "sourceProvider": ref.source,
                    }
                )
            except Exception as e:
                logger.error("failed_to_save_single_reference", index=ref.index, error=str(e))
                # Continue with next? Or fail? Let's fail for now to ensure data integrity
                raise

        logger.info("references_saved_successfully", document_id=document_id)
        return report

    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        error_details = traceback.format_exc()
        logger.error("validate_route_error", document_id=document_id, error=str(exc), traceback=error_details)
        raise HTTPException(status_code=500, detail=f"Reference validation failed: {str(exc)}") from exc
