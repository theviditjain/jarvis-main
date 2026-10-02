"""
QueryEnhancementNode — LangGraph Node.

PURPOSE:
  Rewrites and enriches the raw user query before any retrieval occurs.
  Enhanced queries improve both vector search recall and graph traversal
  precision by expanding abbreviations, resolving pronouns, and adding
  technical context.

POSITION IN WORKFLOW:
  START → [QueryEnhancement] → IntentClassification

INPUTS (from JarvisState):
  - query.original: Raw user input.

OUTPUTS (to JarvisState):
  - enhanced_query: Rewritten, enriched query string.

DESIGN:
  - Calls LLMPort.complete() with a query enhancement prompt.
  - Emits a THINKING event via StreamingPort.
  - Emits a STATUS event when complete.
  - Contains NO prompt text — prompts live in application/prompts/.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class QueryEnhancementNode:
    """
    Rewrites the raw user query into an enriched form for retrieval.

    This node is independently testable. Inject mock ports to unit test
    without LLM or streaming dependencies.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Query Enhancement step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with ``enhanced_query`` populated.

        Note:
            Implementation pending. Returns the original query as-is.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="QueryEnhancement", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="QueryEnhancement",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        # Placeholder: pass through the original query unchanged.
        query = state.get("query", {})
        original = query.get("original", "") if isinstance(query, dict) else ""

        return {
            "enhanced_query": original,
        }
