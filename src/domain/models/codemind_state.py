"""
CodeMindState — LangGraph State Model.

This is the canonical shared state object that flows through every node
of the LangGraph workflow. Each node receives the full state and returns
a partial update.

All fields are Optional so that nodes can incrementally populate the state.
The state is immutable between node boundaries — LangGraph manages copying.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from domain.entities.citation import Citation
from domain.entities.retrieved_node import RetrievedNode
from domain.models.answer import Answer
from domain.models.execution_plan import ExecutionPlan
from domain.models.patch import Patch
from domain.models.tool_result import ToolResult
from domain.value_objects.intent import Intent
from domain.value_objects.query import Query


class CodeMindState(BaseModel):
    """
    The complete shared state of a single CodeMind workflow execution.

    This model is the single source of truth for the state of a request
    as it moves through the LangGraph graph. Every node reads from and
    writes a partial update to this state.

    ─────────────────────────────────────────────────────────────────
    Fields
    ─────────────────────────────────────────────────────────────────

    query               The user's original query, wrapped in a Query VO.
    enhanced_query      The rewritten, enriched query text after Query Enhancement.
    intent              Classified intent produced by Intent Classification.
    execution_plan      Structured plan produced by the Planner node.
    retrieved_nodes     Nodes retrieved from Neo4j and Milvus during Hybrid Retrieval.
    graph_context       Serialised subgraph context assembled by Context Builder.
    repository_context  Raw file content read during Repository Reader (WRITE only).
    tool_results        Accumulated results from every tool call in this execution.
    context             Final assembled context string passed to the LLM.
    reasoning           Intermediate reasoning chain (INTERNAL — never exposed to user).
    answer              Final structured answer returned to the client.
    patch               Proposed code modification (WRITE / HYBRID only).
    citations           All citations produced during this execution.
    need_more_context   Reflection signal: True if another retrieval loop is needed.
    iteration           Current reflection iteration (1-based).
    session_id          Unique identifier for this streaming session.
    repository_id       Repository being queried (optional — may query across all).
    error               Error message if any node encountered an unrecoverable error.
    metadata            Arbitrary metadata for observability and debugging.
    """

    # ── Input ──────────────────────────────────────────────────────────────
    query: Optional[Query] = Field(default=None, description="User query value object.")
    session_id: Optional[str] = Field(
        default=None, description="Unique streaming session identifier."
    )
    repository_id: Optional[str] = Field(
        default=None,
        description="Repository scope for this request.",
    )
    cluster_id: Optional[str] = Field(
        default=None,
        description="Cluster scope for cross-repository isolation.",
    )

    # ── Query Enhancement ──────────────────────────────────────────────────
    enhanced_query: Optional[str] = Field(
        default=None,
        description="Rewritten query produced by Query Enhancement node.",
    )
    is_relevant: Optional[bool] = Field(
        default=None,
        description="Relevance check result from Relevance node.",
    )

    # ── Intent Classification ──────────────────────────────────────────────
    intent: Optional[Intent] = Field(
        default=None,
        description="Classified intent produced by Intent Classification.",
    )

    # ── Planning ──────────────────────────────────────────────────────────
    execution_plan: Optional[ExecutionPlan] = Field(
        default=None,
        description="Structured execution plan produced by the Planner node.",
    )

    # ── Retrieval ─────────────────────────────────────────────────────────
    retrieved_nodes: List[RetrievedNode] = Field(
        default_factory=list,
        description="Nodes retrieved from Neo4j and Milvus.",
    )

    # ── Context Building ──────────────────────────────────────────────────
    graph_context: Optional[str] = Field(
        default=None,
        description="Serialised subgraph context assembled by Context Builder.",
    )
    repository_context: Optional[str] = Field(
        default=None,
        description="Raw file content read from the repository (WRITE only).",
    )
    context: Optional[str] = Field(
        default=None,
        description="Final assembled context string passed to the LLM.",
    )

    # ── Tool Results ──────────────────────────────────────────────────────
    tool_results: List[ToolResult] = Field(
        default_factory=list,
        description="Accumulated results from every tool call.",
    )

    # ── Reasoning & Reflection ────────────────────────────────────────────
    reasoning: Optional[str] = Field(
        default=None,
        description="Intermediate reasoning (INTERNAL — never exposed to clients).",
    )
    need_more_context: bool = Field(
        default=False,
        description="Reflection signal: True if another retrieval loop is needed.",
    )
    iteration: int = Field(
        default=1,
        ge=1,
        description="Current reflection iteration (1-based).",
    )

    # ── Output ────────────────────────────────────────────────────────────
    answer: Optional[Answer] = Field(
        default=None,
        description="Final structured answer returned to the client.",
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="All citations produced during this execution.",
    )

    # ── WRITE / HYBRID ────────────────────────────────────────────────────
    patch: Optional[Patch] = Field(
        default=None,
        description="Proposed code modification (WRITE / HYBRID only).",
    )

    # ── Error & Observability ─────────────────────────────────────────────
    error: Optional[str] = Field(
        default=None,
        description="Error message if any node encountered an unrecoverable error.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata for observability and debugging.",
    )

    class Config:
        # Allow mutation by LangGraph node partial updates
        frozen = False


# Backward compatibility alias
JarvisState = CodeMindState
