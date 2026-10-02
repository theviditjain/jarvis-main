"""
ResponseNode — LangGraph Node.

PURPOSE:
  Produces the final Answer and emits the DONE stream event to signal
  the end of the response stream. This is the terminal node for the
  READ workflow and the shared terminal node for WRITE/HYBRID after
  Git operations.

POSITION IN WORKFLOW:
  READ:   Reflection → [Response] → END
  WRITE:  GitOperations → [Response] → END
  HYBRID: Validation → [Response] → END

INPUTS (from JarvisState):
  - answer:    The Answer object produced by ReasoningNode.
  - citations: All citations accumulated during execution.
  - patch:     The applied Patch object (WRITE/HYBRID only).
  - session_id: Active streaming session.

OUTPUTS (to JarvisState):
  - answer: Finalised Answer with complete citations.

DESIGN:
  - Emits CITATION events for each resolved citation.
  - Emits MERMAID event if a diagram was generated.
  - Emits DONE event to close the stream.
  - Contains NO prompt text.
  - Contains NO LLM calls.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class ResponseNode:
    """
    Finalises the answer and closes the streaming session.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Response step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with finalised ``answer``.

        Note:
            Implementation pending.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="Response", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="Response",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        return {}
