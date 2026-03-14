import google.generativeai as genai
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.config import get_settings
from app.rag.retriever import retrieve_context
from app.rag.prompts import CHAT_SYSTEM, CHAT_USER
from app.utils.logger import get_logger
from app.utils.rate_limiter import limiter

logger = get_logger(__name__)
router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    document_id: str
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


def _format_history(history: list[ChatMessage]) -> str:
    if not history:
        return "No previous conversation."
    lines = []
    for msg in history[-6:]:  # Last 3 exchanges
        role = "USER" if msg.role == "user" else "ASSISTANT"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Conversational RAG endpoint. Retrieves relevant document chunks,
    assembles a contextualized prompt, and queries Gemini for an answer.
    """
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)

    try:
        context, raw_chunks = retrieve_context(
            document_id=body.document_id,
            query=body.message,
        )
    except Exception as exc:
        logger.error("chat_retrieval_failed", document_id=body.document_id, error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to retrieve document context.") from exc

    history_str = _format_history(body.history)

    prompt = CHAT_USER.format(
        retrieved_chunks=context,
        history=history_str,
        user_question=body.message,
    )

    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=CHAT_SYSTEM,
        generation_config=genai.types.GenerationConfig(temperature=0.3),
    )

    try:
        response = model.generate_content(prompt)
        # Check if model blocked response (safety or other reasons)
        if response.candidates and response.candidates[0].finish_reason != 1:
            reason = response.candidates[0].finish_reason
            logger.warning("chat_blocked", reason=reason, document_id=body.document_id)
            raise HTTPException(status_code=400, detail=f"AI blocked the response due to content safety. (Reason: {reason})")
            
        answer = response.text.strip()
    except Exception as exc:
        error_msg = str(exc)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            logger.error("ai_quota_exhausted", error=error_msg, document_id=body.document_id)
            raise HTTPException(status_code=429, detail="AI service quota exhausted. Please try again in a minute.")
        
        logger.error("chat_llm_failed", error=error_msg, document_id=body.document_id)
        raise HTTPException(status_code=500, detail="AI response generation failed.") from exc

    # Build source labels from retrieved chunks
    sources = list({
        chunk["section"].replace("_", " ").title()
        for chunk in raw_chunks
    })

    logger.info("chat_response", document_id=body.document_id, question=body.message[:60])
    return ChatResponse(answer=answer, sources=sources)
