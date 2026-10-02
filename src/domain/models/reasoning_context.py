"""
ReasoningContext — Domain Model.

Bundles the assembled context passed into the Reasoning node.
This model acts as the single input surface for LLM reasoning and
ensures the reasoning layer is fully decoupled from retrieval logic.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from domain.entities.retrieved_node import RetrievedNode


class ReasoningContext(BaseModel):
    """
    Assembled context provided to the Reasoning node.

    Contains the enriched query, retrieved nodes, and any additional
    graph-traversal context assembled by the Context Builder node.
    The reasoning layer treats this as a read-only snapshot.

    Attributes:
        query:              The enhanced (rewritten) user query.
        original_query:     The original unmodified user query.
        retrieved_nodes:    Nodes retrieved from Neo4j and Milvus.
        graph_context:      Serialised graph neighbourhood as text.
        repository_context: Raw file snippets read from the repository.
        max_tokens:         Token budget available for reasoning.
        iteration:          Current reflection iteration (1-based).
    """

    query: str = Field(..., description="Enhanced (rewritten) user query.")
    original_query: str = Field(..., description="Original unmodified query.")
    retrieved_nodes: List[RetrievedNode] = Field(
        default_factory=list,
        description="Nodes retrieved from Neo4j and Milvus.",
    )
    graph_context: Optional[str] = Field(
        default=None,
        description="Serialised graph neighbourhood as text.",
    )
    repository_context: Optional[str] = Field(
        default=None,
        description="Raw file snippets read from the repository.",
    )
    max_tokens: int = Field(
        default=8192,
        description="Token budget available for reasoning.",
    )
    iteration: int = Field(
        default=1,
        ge=1,
        description="Current reflection iteration (1-based).",
    )
