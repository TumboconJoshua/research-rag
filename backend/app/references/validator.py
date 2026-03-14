"""
Reference validation orchestrator.

For each parsed reference:
1. Query Crossref, Semantic Scholar, and OpenAlex in parallel.
2. Score the best match using weighted similarity metrics.
3. Classify into VALID / PARTIALLY_MATCHED / UNVERIFIED / LIKELY_FAKE.
"""
import asyncio
from app.references.schemas import (
    ParsedReference,
    ValidatedReference,
    ValidationReport,
    ReferenceStatus,
)
from app.references.crossref_client import search_crossref, parse_crossref_item
from app.references.semantic_scholar import search_semantic_scholar
from app.references.openalex_client import search_openalex
from app.utils.similarity import title_similarity, author_score, year_match, journal_similarity, compute_confidence
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Confidence thresholds
VALID_THRESHOLD = 0.80
PARTIAL_THRESHOLD = 0.55
UNVERIFIED_THRESHOLD = 0.30


def _status_from_confidence(confidence: float) -> ReferenceStatus:
    if confidence >= VALID_THRESHOLD:
        return ReferenceStatus.VALID
    if confidence >= PARTIAL_THRESHOLD:
        return ReferenceStatus.PARTIALLY_MATCHED
    if confidence >= UNVERIFIED_THRESHOLD:
        return ReferenceStatus.UNVERIFIED
    return ReferenceStatus.LIKELY_FAKE


def _score_candidate(ref: ParsedReference, candidate: dict) -> float:
    """Compute overall confidence that a candidate matches the parsed reference."""
    if not ref.title or not candidate.get("title"):
        return 0.0

    t_sim = title_similarity(ref.title, candidate["title"])
    a_score = author_score(ref.authors, candidate.get("authors", []))
    y_match = year_match(ref.year, candidate.get("year"))
    j_sim = journal_similarity(ref.journal, candidate.get("journal"))

    return compute_confidence(t_sim, a_score, y_match, j_sim)


async def _validate_single_reference(ref: ParsedReference) -> ValidatedReference:
    """Validate one reference against all external APIs."""
    if not ref.title:
        # No title extracted — can't query APIs
        return ValidatedReference(
            **ref.model_dump(),
            status=ReferenceStatus.UNVERIFIED,
            confidence_score=0.0,
            source=None,
        )

    # Query all three APIs concurrently
    crossref_task = search_crossref(ref.title, ref.authors)
    ss_task = search_semantic_scholar(ref.title)
    oa_task = search_openalex(ref.title)

    crossref_raw, ss_results, oa_results = await asyncio.gather(
        crossref_task, ss_task, oa_task, return_exceptions=False
    )

    # Normalize all candidates
    candidates: list[dict] = []
    for item in (crossref_raw or []):
        candidates.append(parse_crossref_item(item))
    candidates.extend(ss_results or [])
    candidates.extend(oa_results or [])

    if not candidates:
        return ValidatedReference(
            **ref.model_dump(),
            status=ReferenceStatus.UNVERIFIED,
            confidence_score=0.0,
            source=None,
        )

    # Find best-matching candidate
    scored = [(c, _score_candidate(ref, c)) for c in candidates]
    best_candidate, best_score = max(scored, key=lambda x: x[1])

    status = _status_from_confidence(best_score)

    return ValidatedReference(
        index=ref.index,
        raw_text=ref.raw_text,
        title=best_candidate.get("title") or ref.title,
        authors=best_candidate.get("authors") or ref.authors,
        year=best_candidate.get("year") or ref.year,
        journal=best_candidate.get("journal") or ref.journal,
        doi=best_candidate.get("doi") or ref.doi,
        status=status,
        confidence_score=round(best_score, 3),
        source=best_candidate.get("source"),
    )


async def validate_references(
    document_id: str,
    parsed_refs: list[ParsedReference],
    concurrency: int = 5,
) -> ValidationReport:
    """
    Validate all extracted references with rate-limited concurrency.

    Args:
        document_id:   The document these references belong to.
        parsed_refs:   List of pre-extracted ParsedReference objects.
        concurrency:   Max simultaneous API calls.

    Returns:
        Complete ValidationReport.
    """
    logger.info("validation_started", document_id=document_id, total=len(parsed_refs))

    # Process in batches to respect API rate limits
    validated: list[ValidatedReference] = []
    semaphore = asyncio.Semaphore(concurrency)

    async def guarded_validate(ref: ParsedReference) -> ValidatedReference:
        async with semaphore:
            try:
                return await _validate_single_reference(ref)
            except Exception as exc:
                logger.error("reference_validation_error", index=ref.index, error=str(exc))
                return ValidatedReference(
                    **ref.model_dump(),
                    status=ReferenceStatus.UNVERIFIED,
                    confidence_score=0.0,
                    source=None,
                )

    tasks = [guarded_validate(ref) for ref in parsed_refs]
    validated = await asyncio.gather(*tasks)

    # Compute summary stats
    status_counts = {s: 0 for s in ReferenceStatus}
    for v in validated:
        status_counts[v.status] += 1

    report = ValidationReport(
        document_id=document_id,
        total_references=len(validated),
        valid_count=status_counts[ReferenceStatus.VALID],
        partially_matched_count=status_counts[ReferenceStatus.PARTIALLY_MATCHED],
        likely_fake_count=status_counts[ReferenceStatus.LIKELY_FAKE],
        unverified_count=status_counts[ReferenceStatus.UNVERIFIED],
        references=list(validated),
    )

    logger.info(
        "validation_complete",
        document_id=document_id,
        valid=report.valid_count,
        fake=report.likely_fake_count,
        unverified=report.unverified_count,
    )
    return report
