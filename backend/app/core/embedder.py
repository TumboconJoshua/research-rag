"""Google Gemini embedding wrapper."""
import asyncio
from functools import lru_cache
import google.generativeai as genai
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _configure_genai():
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Generate embeddings for a batch of texts using Gemini Embeddings API.

    Args:
        texts: List of strings to embed.
        task_type: "RETRIEVAL_DOCUMENT" for indexing, "RETRIEVAL_QUERY" for queries.

    Returns:
        List of embedding vectors (list of floats).
    """
    _configure_genai()
    settings = get_settings()

    try:
        logger.debug("generating_embeddings", count=len(texts))
        result = genai.embed_content(
            model=settings.gemini_embedding_model,
            content=texts,
            task_type=task_type,
        )
        embeddings = result["embedding"]
        
        # API returns a single list when input is a list — normalize
        if isinstance(embeddings[0], float):
            embeddings = [embeddings]
            
        logger.info("embeddings_generated", count=len(embeddings))
        return embeddings
    except Exception as exc:
        error_msg = str(exc)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            logger.error("embedding_quota_exhausted", error=error_msg)
        else:
            logger.error("embedding_failed", error=error_msg)
        raise


def embed_query(query: str) -> list[float]:
    """Embed a single query string for retrieval."""
    results = embed_texts([query], task_type="RETRIEVAL_QUERY")
    return results[0]
