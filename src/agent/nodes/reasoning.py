"""
ReasoningNode — LangGraph Node.

PURPOSE:
  The core reasoning step. Calls the LLM with the assembled context to
  produce a response. The reasoning node:
    - Calls LLMPort.stream() to generate a streaming response.
    - Emits MARKDOWN events as tokens arrive.
    - Extracts citations from the response.
    - Produces a ReasoningContext for the Reflection node.

POSITION IN WORKFLOW:
  READ:   OperationRouter → [Reasoning] → Reflection
  HYBRID: OperationRouter → [Reasoning] → Reflection → PatchPlanner

INPUTS (from JarvisState):
  - context:       Assembled context string from ContextBuilder.
  - enhanced_query: Enriched user query.
  - iteration:     Current reflection iteration.
  - execution_plan: Plan with reasoning parameters.

OUTPUTS (to JarvisState):
  - reasoning:    Internal reasoning chain (NEVER exposed to clients).
  - answer:       Partial Answer object (streamed incrementally).
  - citations:    Extracted citations from the response.

DESIGN:
  - NEVER exposes chain-of-thought reasoning to the client.
  - THINKING events contain only high-level progress summaries.
  - MARKDOWN events carry the actual response content.
  - Contains NO prompt text — prompts live in application/prompts/.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class ReasoningNode:
    """
    Core reasoning step — calls the LLM and streams the response.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Reasoning step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with ``reasoning``, ``answer``, ``citations``.

        Note:
            Implementation pending. Returns a placeholder answer.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="Reasoning", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="Reasoning",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        return {
            "reasoning": "Placeholder reasoning — implementation pending.",
            "answer": {
                "content": "Placeholder answer — reasoning not yet implemented.",
                "citations": [],
                "confidence": 0.0,
                "is_partial": False,
            },
            "citations": [],
        }
