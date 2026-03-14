"""Semantic Scholar API client for reference validation."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.logger import get_logger

logger = get_logger(__name__)

SS_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,authors,year,venue,externalIds"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def search_semantic_scholar(title: str, limit: int = 3) -> list[dict]:
    """
    Search Semantic Scholar for papers matching a title.

    Returns:
        List of normalized paper dicts.
    """
    params = {"query": title, "limit": limit, "fields": FIELDS}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(SS_BASE, params=params)
            response.raise_for_status()
            data = response.json()
            raw_papers = data.get("data", [])
            logger.debug("semantic_scholar_search", title=title[:60], results=len(raw_papers))
            return [_parse_ss_paper(p) for p in raw_papers]
        except httpx.HTTPStatusError as exc:
            logger.warning("ss_http_error", status=exc.response.status_code, title=title[:60])
            return []
        except Exception as exc:
            logger.error("ss_request_failed", error=str(exc), title=title[:60])
            return []


def _parse_ss_paper(paper: dict) -> dict:
    """Normalize a Semantic Scholar paper response."""
    raw_authors = paper.get("authors", [])
    authors = [a.get("name", "") for a in raw_authors]

    doi = None
    ext_ids = paper.get("externalIds", {})
    if ext_ids:
        doi = ext_ids.get("DOI") or ext_ids.get("ArXiv")

    return {
        "title": paper.get("title"),
        "authors": authors,
        "year": paper.get("year"),
        "journal": paper.get("venue"),
        "doi": doi,
        "source": "semantic_scholar",
    }
