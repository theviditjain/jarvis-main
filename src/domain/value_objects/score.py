"""
RelevanceScore — Domain Value Object.

A bounded, normalised floating-point score representing the semantic or
structural relevance of a retrieved node to the current query.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, validator


class RelevanceScore(BaseModel):
    """
    Normalised relevance score in the range [0.0, 1.0].

    Attributes:
        value:  The numeric score value.
        source: The retrieval strategy that produced this score
                (e.g. 'cosine_similarity', 'graph_distance', 'rrf').
    """

    value: float = Field(..., ge=0.0, le=1.0, description="Score in [0, 1].")
    source: str = Field(
        default="unknown",
        description="Retrieval strategy that produced this score.",
    )

    @validator("value")
    def _clamp(cls, v: float) -> float:  # noqa: N805
        return max(0.0, min(1.0, v))

    class Config:
        frozen = True
