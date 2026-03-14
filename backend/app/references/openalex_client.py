"""OpenAlex API client for reference validation."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.logger import get_logger

logger = get_logger(__name__)

OA_BASE = "https://api.openalex.org/works"
HEADERS = {"User-Agent": "ResearchRAG/1.0 (mailto:research.rag.app@gmail.com)"}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def search_openalex(title: str, per_page: int = 3) -> list[dict]:
    """
    Search OpenAlex for works matching a title.

    Returns:
        List of normalized paper dicts.
    """
    params = {"search": title, "per-page": per_page, "select": "title,authorships,publication_year,primary_location,doi"}

    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
        try:
            response = await client.get(OA_BASE, params=params)
            response.raise_for_status()
            data = response.json()
            raw_results = data.get("results", [])
            logger.debug("openalex_search", title=title[:60], results=len(raw_results))
            return [_parse_oa_work(w) for w in raw_results]
        except httpx.HTTPStatusError as exc:
            logger.warning("oa_http_error", status=exc.response.status_code, title=title[:60])
            return []
        except Exception as exc:
            logger.error("oa_request_failed", error=str(exc), title=title[:60])
            return []


def _parse_oa_work(work: dict) -> dict:
    """Normalize an OpenAlex work response."""
    authorships = work.get("authorships", [])
    authors = [
        a.get("author", {}).get("display_name", "")
        for a in authorships
    ]

    primary_loc = work.get("primary_location", {}) or {}
    source = primary_loc.get("source", {}) or {}
    journal = source.get("display_name")

    doi_raw = work.get("doi", "")
    doi = doi_raw.replace("https://doi.org/", "") if doi_raw else None

    return {
        "title": work.get("title"),
        "authors": authors,
        "year": work.get("publication_year"),
        "journal": journal,
        "doi": doi,
        "source": "openalex",
    }
