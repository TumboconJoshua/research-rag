"""Pydantic schemas for research analysis output."""
from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    document_id: str
    research_quality_score: float = Field(ge=0, le=10)
    methodology_score: float = Field(ge=0, le=10)
    citation_integrity: float = Field(ge=0, le=10)
    logical_consistency: float = Field(ge=0, le=10)
    literature_review_score: float = Field(ge=0, le=10)
    data_transparency_score: float = Field(ge=0, le=10)
    strengths: list[str]
    weaknesses: list[str]
    potential_biases: list[str]
    improvement_suggestions: list[str]
    missing_citation_areas: list[str]


class AbstractAnalysis(BaseModel):
    clarity_score: float = Field(ge=0, le=10)
    completeness_score: float = Field(ge=0, le=10)
    has_research_question: bool
    has_methodology_mention: bool
    has_results_preview: bool
    has_conclusion: bool
    word_count: int
    improvement: str
