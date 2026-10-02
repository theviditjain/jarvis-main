"""
IntentClassificationNode — LangGraph Node.

PURPOSE:
  Classifies the user's intent to determine which execution mode the
  workflow should follow: READ, WRITE, or HYBRID.

  Also extracts key entities (class names, method names, file paths)
  from the query to guide downstream retrieval.

POSITION IN WORKFLOW:
  QueryEnhancement → [IntentClassification] → Planner

INPUTS (from JarvisState):
  - enhanced_query: Rewritten query from QueryEnhancement.

OUTPUTS (to JarvisState):
  - intent: Intent value object with execution_mode, category, entities.

DESIGN:
  - Calls LLMPort.complete() with a classification prompt.
  - Parses the structured JSON response into an Intent value object.
  - Emits a THINKING event with the classified mode.
  - Contains NO prompt text — prompts live in application/prompts/.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation
from domain.value_objects.intent import ExecutionMode, Intent


class IntentClassificationNode:
    """
    Classifies user intent and determines the execution mode.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Intent Classification step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with ``intent`` populated.

        Note:
            Implementation pending. Defaults to READ mode.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="IntentClassification", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="IntentClassification",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        # Check manual override from config
        override = container.config.get("workflow.manual_intent_override", "AUTO")
        execution_mode = ExecutionMode.READ
        if override in ["READ", "WRITE", "HYBRID"]:
            execution_mode = ExecutionMode(override)
            logger.info(f"Using manual intent override: {execution_mode}")

        # Placeholder: default to READ mode if AUTO.
        intent = Intent(
            execution_mode=execution_mode,
            category="explain",
            confidence=0.0 if override == "AUTO" else 1.0,
            entities=[],
        )

        return {
            "intent": intent.model_dump(),
        }
