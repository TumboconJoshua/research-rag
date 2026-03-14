"""Research paper quality analyzer using Gemini + RAG retrieval."""
import json
import google.generativeai as genai
from app.config import get_settings
from app.rag.retriever import retrieve_full_document_context
from app.rag.prompts import (
    RESEARCH_ANALYSIS_SYSTEM,
    RESEARCH_ANALYSIS_USER,
    ABSTRACT_ANALYSIS_SYSTEM,
    ABSTRACT_ANALYSIS_USER,
)
from app.analysis.schemas import AnalysisResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_model():
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=RESEARCH_ANALYSIS_SYSTEM,
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )


def _parse_json_response(response_text: str) -> dict:
    """Strip any accidental markdown fences and parse JSON."""
    text = response_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text)


async def analyze_research_paper(text: str) -> dict:
    """
    Run a full AI-powered research quality analysis on provided text.
    """
    logger.info("analysis_started", text_length=len(text))

    model = _get_model()
    prompt = RESEARCH_ANALYSIS_USER.format(context=text[:30000])

    try:
        response = model.generate_content(prompt)
        # Check if the model blocked the response
        if response.candidates and response.candidates[0].finish_reason != 1:
            reason = response.candidates[0].finish_reason
            logger.warning("ai_generation_blocked", reason=reason, safety_ratings=response.prompt_feedback)
            raise ValueError(f"AI content generation blocked. Reason: {reason}")

        raw = response.text
        data = _parse_json_response(raw)

        logger.info("analysis_complete")
        return data

    except json.JSONDecodeError as exc:
        logger.error("analysis_json_parse_error", error=str(exc), raw=response.text[:500] if 'response' in locals() else "N/A")
        raise ValueError(f"AI returned invalid JSON: {exc}") from exc
    except Exception as exc:
        error_msg = str(exc)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            logger.error("ai_quota_exhausted", error=error_msg)
        else:
            logger.error("analysis_failed", error=error_msg)
        raise
