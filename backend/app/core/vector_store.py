"""Numpy/JSON in-process vector store."""
import os
import json
import numpy as np
from app.config import get_settings
from app.utils.logger import get_logger
from app.core.chunker import Chunk
from app.core.embedder import embed_texts, embed_query

logger = get_logger(__name__)


def _get_store_path() -> str:
    settings = get_settings()
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    return os.path.join(settings.chroma_persist_dir, "vector_store.json")


def _load_store() -> dict:
    path = _get_store_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("failed_to_load_store", error=str(e))
    return {}


def _save_store(store: dict) -> None:
    path = _get_store_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False)


def index_chunks(chunks: list[Chunk]) -> None:
    """Embed and store chunks and initialize doc metadata."""
    if not chunks:
        return

    texts = [c.text for c in chunks]
    doc_id = chunks[0].document_id

    # Batch embed
    all_embeddings: list[list[float]] = []
    batch_size = 100
    total_chunks = len(texts)
    
    for i in range(0, total_chunks, batch_size):
        batch = texts[i : i + batch_size]
        logger.info("embedding_batch", current=i, total=total_chunks)
        all_embeddings.extend(embed_texts(batch, task_type="RETRIEVAL_DOCUMENT"))

    store = _load_store()
    
    # Ensure document metadata exists
    if "documents" not in store:
        store["documents"] = {}
    
    # Store/Update document metadata
    store["documents"][doc_id] = {
        "id": doc_id,
        "filename": getattr(chunks[0], "filename", "Unknown"),
        "analysis_report": None, # Cache for later
        "v_report": None,
        "created_at": str(np.datetime64('now'))
    }

    # Index chunks
    if "chunks" not in store:
        store["chunks"] = {}

    # Clear old chunks for this doc
    keys_to_remove = [k for k, v in store["chunks"].items() if v["document_id"] == doc_id]
    for k in keys_to_remove:
        del store["chunks"][k]

    for c, emb in zip(chunks, all_embeddings):
        store["chunks"][c.chunk_id] = {
            "document_id": c.document_id,
            "section": c.section,
            "chunk_index": c.chunk_index,
            "text": c.text,
            "embedding": emb
        }

    _save_store(store)
    logger.info("chunks_indexed", count=len(chunks), doc_id=doc_id)


def save_analysis_report(document_id: str, report: dict) -> None:
    """Cache the analysis result for a document."""
    store = _load_store()
    if "documents" in store and document_id in store["documents"]:
        store["documents"][document_id]["analysis_report"] = report
        _save_store(store)


def get_analysis_report(document_id: str) -> dict | None:
    """Retrieve cached analysis."""
    store = _load_store()
    return store.get("documents", {}).get(document_id, {}).get("analysis_report")


def search_chunks(
    document_id: str,
    query: str,
    top_k: int | None = None,
) -> list[dict]:
    """Retrieve the top_k most relevant chunks for a query."""
    settings = get_settings()
    top_k = top_k or settings.top_k_retrieval
    
    store = _load_store()
    chunks_dict = store.get("chunks", {})
    
    # Filter by document_id
    doc_chunks = [v for v in chunks_dict.values() if v["document_id"] == document_id]
    if not doc_chunks:
        return []

    # Get query embedding
    query_emb = embed_query(query)
    q_vec = np.array(query_emb, dtype=np.float32)

    # Compute cosine similarities
    results = []
    for chunk in doc_chunks:
        c_vec = np.array(chunk["embedding"], dtype=np.float32)
        sim = np.dot(q_vec, c_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(c_vec))
        distance = 1.0 - float(sim)
        results.append((distance, chunk))
    
    results.sort(key=lambda x: x[0])
    top_results = results[:top_k]

    final_chunks = []
    for dist, chunk in top_results:
        final_chunks.append({
            "text": chunk["text"],
            "section": chunk["section"],
            "distance": dist,
        })

    logger.info("chunks_retrieved", count=len(final_chunks))
    return final_chunks

def get_full_text(document_id: str) -> str:
    """Reconstruct full document text from chunks."""
    store = _load_store()
    chunks_dict = store.get("chunks", {})
    doc_chunks = [v for v in chunks_dict.values() if v["document_id"] == document_id]
    doc_chunks.sort(key=lambda x: x["chunk_index"])
    return "\n\n".join([c["text"] for c in doc_chunks])


def delete_document_chunks(document_id: str) -> None:
    store = _load_store()
    
    if "chunks" in store:
        keys_to_remove = [k for k, v in store["chunks"].items() if v["document_id"] == document_id]
        for k in keys_to_remove:
            del store["chunks"][k]
            
    if "documents" in store and document_id in store["documents"]:
        del store["documents"][document_id]
        
    _save_store(store)
    logger.info("document_deleted", document_id=document_id)
