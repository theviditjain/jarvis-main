"""
PlannerNode — LangGraph Node.

PURPOSE:
  Produces a structured ExecutionPlan that directs all subsequent nodes.
  The planner analyses the classified intent and enhanced query to decide:
    - Which graph traversal strategies to use.
    - Which Milvus collections to search.
    - How many retrieval hops are needed.
    - Whether file reads are required.
    - Maximum reflection iterations.

POSITION IN WORKFLOW:
  IntentClassification → [Planner] → HybridRetrieval

INPUTS (from JarvisState):
  - enhanced_query: Enriched query text.
  - intent:         Classified intent with execution_mode.

OUTPUTS (to JarvisState):
  - execution_plan: Structured ExecutionPlan with ordered PlanSteps.

DESIGN:
  - Calls LLMPort.complete() with a planning prompt.
  - Parses structured JSON response into ExecutionPlan.
  - Emits THINKING events with plan summary.
  - Contains NO prompt text — prompts live in application/prompts/.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from domain.models.execution_plan import ExecutionPlan
from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class PlannerNode:
    """
    Produces a structured ExecutionPlan from the classified intent.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Planner step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with ``execution_plan`` populated.

        Note:
            Implementation pending. Returns a minimal default plan.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="Planner", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="Planner",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        # Placeholder: return a minimal default plan.
        intent = state.get("intent", {}) or {}
        execution_mode = (
            intent.get("execution_mode", "READ")
            if isinstance(intent, dict)
            else "READ"
        )

        plan = ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            execution_mode=execution_mode,
            steps=[],
            rationale="Placeholder plan — implementation pending.",
            estimated_hops=1,
            max_iterations=3,
        )

        return {
            "execution_plan": plan.model_dump(),
        }
