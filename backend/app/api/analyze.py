from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.analysis.research_analyzer import analyze_research_paper
from app.analysis.schemas import AnalysisResult
from app.utils.logger import get_logger
from app.utils.rate_limiter import limiter

logger = get_logger(__name__)
router = APIRouter()


@router.post("/analyze-paper/{document_id}", response_model=AnalysisResult)
@limiter.limit("5/minute")
async def analyze_paper_endpoint(request: Request, document_id: str):
    """Perform AI analysis on the document and cache result."""
    from app.core.vector_store import get_analysis_report, save_analysis_report, get_full_text
    
    # Check cache
    cached = get_analysis_report(document_id)
    if cached:
        cached["document_id"] = document_id
        return AnalysisResult(**cached)

    # Get full text for Gemini
    full_text = get_full_text(document_id)
    if not full_text:
        raise HTTPException(status_code=404, detail="Document content not found.")

    try:
        from app.utils.convex_client import get_convex_client
        convex = get_convex_client()

        result = await analyze_research_paper(full_text)
        result["document_id"] = document_id
        
        # Save to local JSON cache (for RAG)
        save_analysis_report(document_id, result)
        
        # Save to Convex for persistence/frontend
        convex.mutation(
            "documents:saveAnalysis",
            {
                "documentId": document_id,
                "researchQualityScore": result["research_quality_score"],
                "methodologyScore": result["methodology_score"],
                "citationIntegrity": result["citation_integrity"],
                "logicalConsistency": result["logical_consistency"],
                "literatureReviewScore": result["literature_review_score"],
                "dataTransparencyScore": result["data_transparency_score"],
                "strengths": result["strengths"],
                "weaknesses": result["weaknesses"],
                "improvementSuggestions": result["improvement_suggestions"],
                "potentialBiases": result["potential_biases"],
                "missingCitationAreas": result["missing_citation_areas"],
            }
        )
        return AnalysisResult(**result)
    except ValueError as exc:
        logger.error("analyze_route_error_value", document_id=document_id, error=str(exc))
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("analyze_route_error_general", document_id=document_id, error=str(exc))
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.") from exc
