"""
ReflectionNode — LangGraph Node.

PURPOSE:
  Evaluates the quality of the reasoning output and decides whether
  another retrieval loop is necessary. This enables self-correction:
  if the reasoning layer determines the context is insufficient, the
  workflow loops back to HybridRetrieval with a refined query.

POSITION IN WORKFLOW:
  Reasoning → [Reflection] → (HybridRetrieval | Response)

INPUTS (from JarvisState):
  - reasoning:       Internal reasoning chain from ReasoningNode.
  - answer:          Current partial answer.
  - retrieved_nodes: Nodes retrieved so far.
  - iteration:       Current iteration count.
  - execution_plan:  Plan with max_iterations constraint.

OUTPUTS (to JarvisState):
  - need_more_context: True if another retrieval loop is needed.
  - iteration:         Incremented iteration count.
  - enhanced_query:    Refined query for the next retrieval loop (if needed).

DESIGN:
  - Calls LLMPort.complete() with a reflection prompt.
  - Respects max_iterations from the ExecutionPlan.
  - Emits THINKING event with reflection decision rationale.
  - Contains NO prompt text — prompts live in application/prompts/.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class ReflectionNode:
    """
    Evaluates reasoning quality and gates the retrieval loop.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Reflection step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with ``need_more_context`` and ``iteration``.

        Note:
            Implementation pending. Always returns done (no re-retrieval).
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="Reflection", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="Reflection",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        current_iteration = state.get("iteration", 1) or 1
        return {
            "need_more_context": False,
            "iteration": current_iteration + 1,
        }
