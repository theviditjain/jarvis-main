"""
Answer — Domain Model.

The final structured output produced by the reasoning layer and
delivered to the client. An Answer bundles the markdown content,
Mermaid diagram (optional), and all supporting citations.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from domain.entities.citation import Citation


class Answer(BaseModel):
    """
    The structured response produced by the reasoning workflow.

    Attributes:
        content:        Primary markdown-formatted answer text.
        mermaid:        Optional Mermaid diagram string for visual representation.
        citations:      List of source attributions backing claims in the answer.
        confidence:     Overall confidence score for this answer [0, 1].
        is_partial:     True if the answer is being streamed and is not yet complete.
        needs_followup: True if the reasoning layer determined a follow-up is needed.
        followup_hint:  Suggested follow-up question if ``needs_followup`` is True.
    """

    content: str = Field(..., description="Primary markdown-formatted answer text.")
    mermaid: Optional[str] = Field(
        default=None,
        description="Optional Mermaid diagram string.",
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="Source attributions backing the answer.",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score [0, 1].",
    )
    is_partial: bool = Field(
        default=False,
        description="True while the answer is being streamed.",
    )
    needs_followup: bool = Field(
        default=False,
        description="True if a follow-up question is recommended.",
    )
    followup_hint: Optional[str] = Field(
        default=None,
        description="Suggested follow-up question.",
    )
