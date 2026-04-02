"""
Pydantic models for request/response validation.
New schema: document classification, bullet-point summaries, structured sentiment.
"""

from typing import List
from pydantic import BaseModel, Field


class SummaryResult(BaseModel):
    bullets: List[str] = Field(default_factory=list, description="Key bullet points from the document")
    tldr: str = Field(default="", description="One-line TL;DR summary")


class EntitySet(BaseModel):
    people: List[str] = Field(default_factory=list, description="Names of people")
    organizations: List[str] = Field(default_factory=list, description="Company/org names")
    dates: List[str] = Field(default_factory=list, description="Date references")
    amounts: List[str] = Field(default_factory=list, description="Monetary values")


class SentimentResult(BaseModel):
    label: str = Field(description="positive, negative, or neutral")
    confidence: int = Field(ge=0, le=100, description="Confidence score 0–100")
    reason: str = Field(default="", description="Brief reasoning for the sentiment")


class AnalysisResponse(BaseModel):
    status: str = Field(default="success")
    filename: str
    file_type: str
    word_count: int
    document_type: str = Field(default="General", description="Document classification")
    summary: SummaryResult
    entities: EntitySet
    sentiment: SentimentResult
    processing_steps: List[str] = Field(default_factory=list)
    processing_time_ms: float


class ErrorResponse(BaseModel):
    status: str = Field(default="error")
    detail: str
    message: str
