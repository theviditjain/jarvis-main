"""
OperationRouterNode — LangGraph Node.

PURPOSE:
  Routes the workflow to the correct execution branch based on the
  classified intent's execution_mode:
    - READ   → reasoning node
    - WRITE  → patch_planner node
    - HYBRID → reasoning node (reasoning precedes patch planning)

  This node performs no computation — it exists purely as a routing
  waypoint that makes the conditional graph branching explicit and
  independently testable.

POSITION IN WORKFLOW:
  ContextBuilder → [OperationRouter] → (READ|WRITE|HYBRID branch)

INPUTS (from JarvisState):
  - intent.execution_mode: The classified execution mode.

OUTPUTS (to JarvisState):
  - No state mutation. Routing happens via conditional edge function.

DESIGN:
  - No LLM calls. No I/O. Pure pass-through.
  - The actual routing decision lives in the ``_route_by_mode`` function
    in application/graph/__init__.py.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class OperationRouterNode:
    """
    Pass-through routing node — activates the correct workflow branch.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Operation Router step.

        This is a pass-through node. The routing decision is made by
        the ``_route_by_mode`` conditional edge function.

        Args:
            state: Current LangGraph state.

        Returns:
            Empty dict — no state mutation.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="OperationRouter", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="OperationRouter",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        return {}
