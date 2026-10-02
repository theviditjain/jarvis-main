"""
Query — Domain Value Object.

Immutable representation of a user query at various stages of processing.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Query(BaseModel):
    """
    Immutable representation of a user query.

    Attributes:
        original:  The raw user input as received by the API.
        enhanced:  The rewritten, enriched query produced by Query Enhancement.
        language:  Detected programming language context, if any.
    """

    original: str = Field(..., description="Raw user input.")
    enhanced: str = Field(
        default="",
        description="Rewritten query produced by the Query Enhancement node.",
    )
    language: str = Field(
        default="",
        description="Detected programming language context.",
    )

    class Config:
        frozen = True
