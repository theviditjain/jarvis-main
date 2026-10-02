"""
Intent & ExecutionMode — Domain Value Objects.

Intent captures what the user wants to do. ExecutionMode determines
which branch of the LangGraph workflow is activated.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    """
    The execution mode activated by the Intent Classification node.

    Attributes:
        READ:   Pure read — query the codebase and answer questions.
        WRITE:  Pure write — modify repository files via patch generation.
        HYBRID: Read then write — understand context before modifying.
    """

    READ = "READ"
    WRITE = "WRITE"
    HYBRID = "HYBRID"


class Intent(BaseModel):
    """
    Classified intent of the user's query.

    Attributes:
        execution_mode: READ, WRITE, or HYBRID.
        category:       High-level category (e.g. 'explain', 'implement', 'refactor').
        confidence:     Classifier confidence score [0, 1].
        entities:       Key entities extracted from the query (class names, etc.).
        rationale:      Human-readable explanation of the classification.
    """

    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.READ,
        description="Execution mode: READ | WRITE | HYBRID.",
    )
    category: str = Field(
        default="explain",
        description="High-level intent category.",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Classifier confidence score [0, 1].",
    )
    entities: list[str] = Field(
        default_factory=list,
        description="Key entities extracted from the query.",
    )
    rationale: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of the classification.",
    )

    class Config:
        frozen = True
