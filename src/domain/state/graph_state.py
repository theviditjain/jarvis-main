"""
LangGraph State Annotation.

Defines the TypedDict-based state annotation used by LangGraph
to perform incremental state merging between nodes. This wraps
the Pydantic CodeMindState for compatibility with LangGraph's
annotation system.
"""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class GraphStateAnnotation(TypedDict, total=False):
    """
    LangGraph-compatible state annotation for the CodeMind workflow.

    Each field corresponds to a field in CodeMindState. Fields that use
    list accumulation (retrieved_nodes, tool_results, citations) use
    the ``add_messages`` reducer to append rather than replace.

    This TypedDict is the type passed to ``StateGraph(GraphStateAnnotation)``.
    """

    # Input
    session_id: Optional[str]
    repository_id: Optional[str]
    cluster_id: Optional[str]
    query: Optional[Dict[str, Any]]

    # Query Enhancement
    enhanced_query: Optional[str]
    is_relevant: Optional[bool]

    # Intent Classification
    intent: Optional[Dict[str, Any]]

    # Planning
    execution_plan: Optional[Dict[str, Any]]

    # Retrieval — list fields use append semantics
    retrieved_nodes: Annotated[List[Dict[str, Any]], add_messages]

    # Context Building
    graph_context: Optional[str]
    repository_context: Optional[str]
    context: Optional[str]

    # Tool Results — append semantics
    tool_results: Annotated[List[Dict[str, Any]], add_messages]

    # Reasoning
    reasoning: Optional[str]
    need_more_context: bool
    iteration: int

    # Output
    answer: Optional[Dict[str, Any]]
    citations: Annotated[List[Dict[str, Any]], add_messages]
    patch: Optional[Dict[str, Any]]

    # Observability
    error: Optional[str]
    metadata: Dict[str, Any]
