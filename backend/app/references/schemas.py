"""Pydantic schemas for reference validation output."""
from enum import Enum
from pydantic import BaseModel, Field


class ReferenceStatus(str, Enum):
    VALID = "VALID"
    PARTIALLY_MATCHED = "PARTIALLY_MATCHED"
    LIKELY_FAKE = "LIKELY_FAKE"
    UNVERIFIED = "UNVERIFIED"


class ParsedReference(BaseModel):
    """A reference extracted and normalized from the document."""
    index: int
    raw_text: str
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    journal: str | None = None
    doi: str | None = None


class ValidatedReference(BaseModel):
    """A reference after API validation with confidence scoring."""
    index: int
    raw_text: str
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    journal: str | None = None
    doi: str | None = None
    status: ReferenceStatus = ReferenceStatus.UNVERIFIED
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    source: str | None = None  # crossref | semantic_scholar | openalex | ai_flagged


class ValidationReport(BaseModel):
    document_id: str
    total_references: int
    valid_count: int
    partially_matched_count: int
    likely_fake_count: int
    unverified_count: int
    references: list[ValidatedReference]
