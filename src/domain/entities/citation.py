"""
Citation — Domain Entity.

Represents a source attribution linking a claim in the AI response to
a specific location in a repository. Citations make the AI output
verifiable and traceable to real source code.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """
    A traceable reference from an AI-generated answer back to source code.

    Every claim made by the reasoning layer that can be attributed to a
    specific code element should carry a ``Citation``. This enables the
    frontend to render linked source-code references alongside responses.

    Attributes:
        node_id:        The Neo4j node ID of the cited element.
        repository_id:  Repository the citation originates from.
        file_path:      Repository-relative path to the source file.
        line_start:     First line number of the cited region (1-indexed).
        line_end:       Last line number of the cited region (1-indexed).
        element_name:   Human-readable qualified name of the element.
        node_type:      Type of the cited code element.
        relevance_score: Confidence score for this citation.
        snippet:        Optional short code snippet for inline display.
    """

    node_id: str = Field(..., description="Neo4j node ID of the cited element.")
    repository_id: str = Field(
        ..., description="Repository the citation originates from."
    )
    file_path: str = Field(
        ..., description="Repository-relative path to the source file."
    )
    line_start: Optional[int] = Field(
        default=None, ge=1, description="First line number (1-indexed)."
    )
    line_end: Optional[int] = Field(
        default=None, ge=1, description="Last line number (1-indexed)."
    )
    element_name: str = Field(
        ..., description="Qualified name of the cited code element."
    )
    node_type: str = Field(
        ..., description="Type of the cited code element."
    )
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this citation.",
    )
    snippet: Optional[str] = Field(
        default=None,
        description="Short code snippet for inline display.",
    )

    class Config:
        frozen = True
