"""
RelevanceNode — LangGraph Node.

PURPOSE:
  Acts as a basic guardrail to check if the user query is relevant to the repository.
  If the query is off-topic, it populates the answer early and sets is_relevant = False.

POSITION IN WORKFLOW:
  START -> [Relevance] -> QueryEnhancement
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation
from domain.models.answer import Answer


class RelevanceNode:
    """
    Evaluates if the user query is relevant to the repository.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Relevance check.

        Args:
            state: Current LangGraph state.
            config: Runnable configuration.

        Returns:
            Partial state update with ``is_relevant`` populated, and potentially ``answer``.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="Relevance", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="Relevance",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        # Check if node is disabled via config (handled by wrapper normally, but double check)
        is_enabled = container.config.get("workflow.nodes_enabled.relevance", True)
        if not is_enabled:
            return {}

        # Here we would normally call the LLMPort. For now, this is a placeholder implementation.
        # In a real scenario, LLM decides True/False based on the query.
        # We will assume True by default unless it's obviously gibberish, but as a placeholder, we just set True.
        
        # To simulate a check, we could check if query is present.
        query_text = ""
        query_obj = state.get("query")
        if query_obj and isinstance(query_obj, dict):
            query_text = query_obj.get("text", "")
        elif hasattr(query_obj, "text"):
            query_text = query_obj.text
            
        # Very basic mock check: if user says "capital of", we reject.
        is_relevant = True
        answer_payload = None
        
        if "capital of" in query_text.lower() or "weather in" in query_text.lower():
            is_relevant = False
            
        if not is_relevant:
            answer_payload = Answer(
                content="I can only assist with questions related to this codebase. Please ask a relevant programming or architecture question.",
                format="markdown",
                confidence=1.0,
            ).model_dump()
            logger.warning(f"Query flagged as irrelevant: {query_text}")

        update = {"is_relevant": is_relevant}
        if answer_payload:
            update["answer"] = answer_payload
            
        return update
