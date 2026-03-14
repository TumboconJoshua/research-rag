"""Reference section extractor and citation parser using regex + NLP heuristics."""
import re
from app.references.schemas import ParsedReference
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Patterns to detect start of references section
REFERENCES_SECTION_PATTERNS = [
    r"(?im)^\s*references?\s*$",
    r"(?im)^\s*bibliography\s*$",
    r"(?im)^\s*works?\s+cited\s*$",
    r"(?im)^\s*\d+\.\s+references?\s*$",
]

# Citation entry patterns (numbered, bracketed, or hanging indent)
CITATION_PATTERNS = [
    # IEEE: [1] Authors, "Title," ...
    r"^\[(\d+)\]\s+(.+?)(?=^\[\d+\]|\Z)",
    # Numbered: 1. Authors (Year). Title...
    r"^(\d+)\.\s+(.+?)(?=^\d+\.|\Z)",
    # APA/Harvard hanging: Authors (Year). Title...
    r"^([A-Z][a-záéíóú\-]+(?:,\s+[A-Z]\.)+.+?)(?=^[A-Z][a-záéíóú\-]+(?:,\s+[A-Z]\.)|\Z)",
]

# Regex patterns to extract citation fields
YEAR_PATTERN = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
DOI_PATTERN = re.compile(r"10\.\d{4,}/[^\s]+", re.IGNORECASE)
AUTHOR_LIST_PATTERN = re.compile(
    r"^((?:[A-Z][a-záéíóú\-]+(?:,\s+[A-Z]\.(?:\s*[A-Z]\.)?)?(?:,\s+|\s+&\s+|\s+and\s+))*"
    r"[A-Z][a-záéíóú\-]+(?:,\s+[A-Z]\.(?:\s*[A-Z]\.)?)?)\s*[\(\.,]"
)


def _extract_references_section(text: str) -> str:
    """Find and return the references section of the document."""
    for pattern in REFERENCES_SECTION_PATTERNS:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return text[match.start():]
    # Fallback: last 20% of document
    cutoff = int(len(text) * 0.78)
    logger.warning("references_section_not_found_using_fallback")
    return text[cutoff:]


def _split_citations(refs_text: str) -> list[str]:
    """
    Split the references section into individual citation strings.
    Handles IEEE [N], numbered N., and paragraph-style citations.
    """
    # Try IEEE bracketed style first
    entries = re.split(r"\n(?=\[\d+\])", refs_text)
    if len(entries) > 3:
        return [e.strip() for e in entries if e.strip()]

    # Try numbered style
    entries = re.split(r"\n(?=\d{1,3}\.)", refs_text)
    if len(entries) > 3:
        return [e.strip() for e in entries if e.strip()]

    # Fallback: split by blank lines
    entries = re.split(r"\n\s*\n", refs_text)
    return [e.strip() for e in entries if e.strip() and len(e.strip()) > 20]


def _extract_year(text: str) -> int | None:
    match = YEAR_PATTERN.search(text)
    return int(match.group(1)) if match else None


def _extract_doi(text: str) -> str | None:
    match = DOI_PATTERN.search(text)
    return match.group(0).rstrip(".") if match else None


def _extract_title(text: str) -> str | None:
    """
    Heuristic title extraction:
    - Look for quoted text "Title"
    - Look for text between year and journal separator
    """
    # Quoted title
    quoted = re.search(r'["""](.+?)["""]', text)
    if quoted:
        return quoted.group(1).strip()

    # Title often follows year or period after authors
    # Try to grab text between first . and next . or journal indicator
    parts = text.split(".")
    if len(parts) >= 2:
        candidate = parts[1].strip()
        # Filter out short fragments or year fragments
        if len(candidate) > 15 and not YEAR_PATTERN.search(candidate[:8]):
            return candidate
    return None


def _extract_authors(text: str) -> list[str]:
    """
    Extract author list from the beginning of a citation string.
    Returns list of author name strings.
    """
    # Try explicit "by" keyword
    by_match = re.search(r"\bby\s+([A-Z][^,\.]+(?:,\s+[A-Z][^,\.]+)*)", text, re.IGNORECASE)
    if by_match:
        return [a.strip() for a in by_match.group(1).split(",") if a.strip()]

    # Try the common surname, initial pattern
    match = AUTHOR_LIST_PATTERN.match(text.strip())
    if match:
        raw = match.group(1)
        # Split on " and " / "&" / ", " between complete names
        authors = re.split(r",?\s+(?:and|&)\s+|;\s+", raw)
        return [a.strip() for a in authors if a.strip()]

    return []


def _extract_journal(text: str) -> str | None:
    """
    Look for italic-style or explicit journal identifiers.
    Common patterns: "In <Journal>", "Journal of ...", "Proceedings of ..."
    """
    journal_patterns = [
        r"\bIn:?\s+([A-Z][^,\.]+(?:Journal|Conference|Proceedings|Review|Transactions|Letters)[^,\.]*)",
        r"((?:Journal|Conference|Proceedings|Review|Transactions|Letters|Symposium|Workshop)\s+(?:of|on|for)\s+[^,\.]+)",
        r"((?:Nature|Science|Cell|PLOS|arXiv)[^,\.]*)",
    ]
    for pattern in journal_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_references(text: str) -> list[ParsedReference]:
    """
    Extract and parse all references from a document's full text.

    Returns:
        List of ParsedReference objects with best-effort field extraction.
    """
    refs_section = _extract_references_section(text)
    citation_strings = _split_citations(refs_section)

    parsed: list[ParsedReference] = []
    for i, raw in enumerate(citation_strings[:100]):  # cap at 100 refs
        # Skip too-short lines (likely page headers/footers)
        if len(raw) < 30:
            continue

        parsed.append(
            ParsedReference(
                index=i,
                raw_text=raw,
                title=_extract_title(raw),
                authors=_extract_authors(raw),
                year=_extract_year(raw),
                journal=_extract_journal(raw),
                doi=_extract_doi(raw),
            )
        )

    logger.info("references_extracted", total=len(parsed))
    return parsed
