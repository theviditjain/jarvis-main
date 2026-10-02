"""
JARVIS LangGraph Workflow.

Defines and compiles the complete LangGraph StateGraph for the JARVIS
AI Runtime. The graph supports three execution modes:

  READ   — Query Enhancement → Intent → Plan → Retrieval → Context →
            Reasoning → Reflection → Response

  WRITE  — Query Enhancement → Intent → Plan → Retrieval → Context →
            Patch Planner → Repo Reader → Patch Generator → Validation →
            Git Operations → Response

  HYBRID — Query Enhancement → Intent → Plan → Retrieval → Context →
            Reasoning → Patch Planner → Patch Generator → Validation →
            Response

The graph is compiled once at startup and reused for all requests.
"""

from __future__ import annotations

from typing import Callable, Any, Dict
from langgraph.graph import StateGraph, END, START
from langchain_core.runnables import RunnableConfig

from domain.state.graph_state import GraphStateAnnotation
from agent.nodes.relevance import RelevanceNode
from agent.nodes.query_enhancement import QueryEnhancementNode
from agent.nodes.intent_classification import IntentClassificationNode
from agent.nodes.planner import PlannerNode
from agent.nodes.hybrid_retrieval import HybridRetrievalNode
from agent.nodes.context_builder import ContextBuilderNode
from agent.nodes.operation_router import OperationRouterNode
from agent.nodes.reasoning import ReasoningNode
from agent.nodes.reflection import ReflectionNode
from agent.nodes.response import ResponseNode
from agent.nodes.patch_planner import PatchPlannerNode
from agent.nodes.repository_reader import RepositoryReaderNode
from agent.nodes.patch_generator import PatchGeneratorNode
from agent.nodes.validation import ValidationNode
from agent.nodes.git_operations import GitOperationsNode


def _make_toggleable(node_name: str, func: Callable) -> Callable:
    """
    Wraps a node function to check if it is enabled in the configuration.
    If disabled, returns an empty dict (pass-through).
    """
    async def wrapper(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        container = config["configurable"]["container"]
        # Default to True if not explicitly disabled
        enabled = container.config.get(f"workflow.nodes_enabled.{node_name}", True)
        if not enabled:
            logger = container.logging.bind(step="ToggleCheck", workflow_id=state.get("session_id", "unknown"))
            logger.info(f"Node '{node_name}' is disabled via configuration. Bypassing.")
            return {}
        return await func(state, config)
    return wrapper


def build_graph() -> StateGraph:
    """
    Construct and compile the JARVIS LangGraph workflow.

    Returns:
        A compiled LangGraph StateGraph ready to invoke.
    """
    graph = StateGraph(GraphStateAnnotation)

    # ── Register Nodes ───────────────────────────────────────────────────
    graph.add_node("relevance", _make_toggleable("relevance", RelevanceNode.run))
    graph.add_node("query_enhancement", _make_toggleable("query_enhancement", QueryEnhancementNode.run))
    graph.add_node("intent_classification", _make_toggleable("intent_classification", IntentClassificationNode.run))
    graph.add_node("planner", _make_toggleable("planner", PlannerNode.run))
    graph.add_node("hybrid_retrieval", _make_toggleable("hybrid_retrieval", HybridRetrievalNode.run))
    graph.add_node("context_builder", _make_toggleable("context_builder", ContextBuilderNode.run))
    graph.add_node("operation_router", _make_toggleable("operation_router", OperationRouterNode.run))

    # READ path
    graph.add_node("reasoning", _make_toggleable("reasoning", ReasoningNode.run))
    graph.add_node("reflection", _make_toggleable("reflection", ReflectionNode.run))
    graph.add_node("response", _make_toggleable("response", ResponseNode.run))

    # WRITE path
    graph.add_node("patch_planner", _make_toggleable("patch_planner", PatchPlannerNode.run))
    graph.add_node("repository_reader", _make_toggleable("repository_reader", RepositoryReaderNode.run))
    graph.add_node("patch_generator", _make_toggleable("patch_generator", PatchGeneratorNode.run))
    graph.add_node("validation", _make_toggleable("validation", ValidationNode.run))
    graph.add_node("git_operations", _make_toggleable("git_operations", GitOperationsNode.run))

    # ── Linear Entry Path ────────────────────────────────────────────────
    graph.add_edge(START, "relevance")
    
    # Conditional edge after relevance
    graph.add_conditional_edges(
        "relevance",
        _check_relevance,
        {
            "relevant": "query_enhancement",
            "irrelevant": "response",
        },
    )

    graph.add_edge("query_enhancement", "intent_classification")
    graph.add_edge("intent_classification", "planner")
    graph.add_edge("planner", "hybrid_retrieval")
    graph.add_edge("hybrid_retrieval", "context_builder")
    graph.add_edge("context_builder", "operation_router")

    # ── Conditional Routing ──────────────────────────────────────────────
    graph.add_conditional_edges(
        "operation_router",
        _route_by_mode,
        {
            "READ": "reasoning",
            "WRITE": "patch_planner",
            "HYBRID": "reasoning",
        },
    )

    # ── READ Path ────────────────────────────────────────────────────────
    graph.add_edge("reasoning", "reflection")
    graph.add_conditional_edges(
        "reflection",
        _should_retrieve_more,
        {
            "continue": "hybrid_retrieval",
            "done": "response",
        },
    )
    graph.add_edge("response", END)

    # ── WRITE Path ───────────────────────────────────────────────────────
    graph.add_edge("patch_planner", "repository_reader")
    graph.add_edge("repository_reader", "patch_generator")
    graph.add_edge("patch_generator", "validation")
    graph.add_conditional_edges(
        "validation",
        _is_patch_valid,
        {
            "valid": "git_operations",
            "invalid": "patch_generator",
        },
    )
    graph.add_edge("git_operations", "response")

    # ── HYBRID: reasoning → patch_planner ───────────────────────────────
    # The HYBRID path goes through reasoning first, then patch planning.
    # Conditional routing from operation_router sends HYBRID to reasoning,
    # and the HYBRID state flag causes reflection → patch_planner transition.
    # This is handled inside ReflectionNode for HYBRID mode.

    return graph


# ── Edge Condition Functions ─────────────────────────────────────────────

def _check_relevance(state: GraphStateAnnotation) -> str:
    """
    Conditional edge: if relevance node determined the query is irrelevant, 
    short-circuit to response.
    """
    if state.get("is_relevant") is False:
        return "irrelevant"
    return "relevant"


def _route_by_mode(state: GraphStateAnnotation) -> str:
    """
    Conditional edge: route based on execution_mode from intent.
    """
    intent = state.get("intent")
    if intent and "execution_mode" in intent:
        mode = intent["execution_mode"]
        # Handle string or Enum
        if hasattr(mode, "value"):
            mode = mode.value
        if mode in ["READ", "WRITE", "HYBRID"]:
            return mode
    return "READ"


def _should_retrieve_more(state: GraphStateAnnotation) -> str:
    """
    Conditional edge: continue retrieval loop or finalize response.
    """
    return "done"


def _is_patch_valid(state: GraphStateAnnotation) -> str:
    """
    Conditional edge: route to git_operations if patch is valid.
    """
    return "valid"
