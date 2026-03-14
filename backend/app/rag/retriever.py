"""RAG retriever — fetches relevant chunks and formats context for the LLM."""
from app.core.vector_store import search_chunks
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def retrieve_context(document_id: str, query: str, top_k: int | None = None) -> tuple[str, list[dict]]:
    """
    Retrieve top-K relevant chunks from the vector store and format them
    as a single context string for prompt injection.

    Returns:
        Tuple of (formatted_context_string, raw_chunks_list)
    """
    settings = get_settings()
    top_k = top_k or settings.top_k_retrieval

    chunks = search_chunks(document_id=document_id, query=query, top_k=top_k)

    if not chunks:
        return "No relevant context found in the document.", []

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        section_label = chunk["section"].replace("_", " ").title()
        context_parts.append(
            f"[Excerpt {i} — {section_label}]\n{chunk['text']}"
        )

    formatted_context = "\n\n---\n\n".join(context_parts)
    return formatted_context, chunks


def retrieve_full_document_context(document_id: str, max_chars: int = 12000) -> str:
    """
    Retrieve a broad representative context from the document for full analysis.
    Queries multiple representative aspects to maximize coverage.
    """
    queries = [
        "abstract research question hypothesis",
        "methodology experimental design approach",
        "results findings data analysis",
        "discussion conclusion implications",
        "limitations future work",
    ]

    seen_indices: set[int] = set()
    all_chunks: list[dict] = []

    for query in queries:
        chunks = search_chunks(document_id=document_id, query=query, top_k=3)
        for chunk in chunks:
            idx = chunk["chunk_index"]
            if idx not in seen_indices:
                seen_indices.add(idx)
                all_chunks.append(chunk)

    # Sort by chunk index to preserve document order
    all_chunks.sort(key=lambda c: c["chunk_index"])

    context_parts = []
    total_chars = 0
    for chunk in all_chunks:
        if total_chars + len(chunk["text"]) > max_chars:
            break
        section_label = chunk["section"].replace("_", " ").title()
        context_parts.append(f"[{section_label}]\n{chunk['text']}")
        total_chars += len(chunk["text"])

    return "\n\n".join(context_parts)
