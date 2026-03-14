"""String similarity utilities for reference validation."""
from rapidfuzz import fuzz


def title_similarity(a: str, b: str) -> float:
    """Compute normalized token sort ratio between two title strings."""
    if not a or not b:
        return 0.0
    return fuzz.token_sort_ratio(a.lower().strip(), b.lower().strip()) / 100.0


def author_score(extracted: list[str], found: list[str]) -> float:
    """
    Compute match score between two author lists.
    Normalizes to last names and computes intersection ratio.
    """
    if not extracted or not found:
        return 0.0

    def normalize_author(name: str) -> str:
        parts = name.replace(",", " ").split()
        return parts[0].lower() if parts else ""

    extracted_norm = {normalize_author(a) for a in extracted}
    found_norm = {normalize_author(a) for a in found}

    if not extracted_norm or not found_norm:
        return 0.0

    intersection = extracted_norm & found_norm
    union = extracted_norm | found_norm
    return len(intersection) / len(union)


def year_match(extracted_year: int | None, found_year: int | None) -> float:
    """Exact year match returns 1.0, off-by-one returns 0.5, else 0.0."""
    if extracted_year is None or found_year is None:
        return 0.0
    if extracted_year == found_year:
        return 1.0
    if abs(extracted_year - found_year) == 1:
        return 0.5
    return 0.0


def journal_similarity(a: str | None, b: str | None) -> float:
    """Fuzzy match between journal/venue names."""
    if not a or not b:
        return 0.0
    return fuzz.partial_ratio(a.lower().strip(), b.lower().strip()) / 100.0


def compute_confidence(
    title_sim: float,
    auth_score: float,
    yr_match: float,
    jour_sim: float,
) -> float:
    """
    Weighted confidence score for a reference match.
    Weights: title=0.45, authors=0.25, year=0.15, journal=0.15
    """
    return (
        title_sim  * 0.45
        + auth_score * 0.25
        + yr_match   * 0.15
        + jour_sim   * 0.15
    )
