"""Crossref API client for reference validation."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.logger import get_logger

logger = get_logger(__name__)

CROSSREF_BASE = "https://api.crossref.org/works"
HEADERS = {"User-Agent": "ResearchRAG/1.0 (mailto:research.rag.app@gmail.com)"}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def search_crossref(
    title: str,
    authors: list[str] | None = None,
    rows: int = 3,
) -> list[dict]:
    """
    Search Crossref for works matching a title and optional author list.

    Returns:
        List of raw Crossref work items.
    """
    params: dict = {
        "query.title": title,
        "rows": rows,
        "select": "DOI,title,author,published,container-title",
    }
    if authors:
        params["query.author"] = " ".join(authors[:3])  # First 3 authors max

    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
        try:
            response = await client.get(CROSSREF_BASE, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("message", {}).get("items", [])
            logger.debug("crossref_search", title=title[:60], results=len(items))
            return items
        except httpx.HTTPStatusError as exc:
            logger.warning("crossref_http_error", status=exc.response.status_code, title=title[:60])
            return []
        except Exception as exc:
            logger.error("crossref_request_failed", error=str(exc), title=title[:60])
            return []


def parse_crossref_item(item: dict) -> dict:
    """Extract normalized fields from a Crossref work item."""
    titles: list = item.get("title", [])
    title = titles[0] if titles else None

    raw_authors = item.get("author", [])
    authors = [
        f"{a.get('family', '')} {a.get('given', '')}".strip()
        for a in raw_authors
    ]

    pub_date = item.get("published", {})
    date_parts = pub_date.get("date-parts", [[]])
    year = date_parts[0][0] if date_parts and date_parts[0] else None

    containers: list = item.get("container-title", [])
    journal = containers[0] if containers else None

    doi = item.get("DOI")

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "doi": doi,
        "source": "crossref",
    }
