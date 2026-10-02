"""
GitOperationsNode — LangGraph Node.

PURPOSE:
  Applies a validated patch to the repository via GitPort. This is the
  only node that performs Git operations. After a successful apply:
    1. The patch is committed to a new branch.
    2. A pull request is created.
    3. Changed file paths are recorded for jarvis-parser re-indexing.

  jarvis-parser re-indexing is NOT triggered by this runtime.
  The runtime records the changed files in the response for the
  caller (jarvis-platform) to trigger re-indexing.

POSITION IN WORKFLOW:
  Validation → [GitOperations] → Response (WRITE only)

INPUTS (from JarvisState):
  - patch: Validated Patch object.
  - repository_id: Target repository.

OUTPUTS (to JarvisState):
  - answer: Updated with PR URL and commit SHA.

DESIGN:
  - Calls GitPort.apply_patch() to commit the patch.
  - Calls GitPort.create_pull_request() to open a PR.
  - Emits TOOL events for each Git operation.
  - Emits THINKING event with PR creation summary.
  - Contains NO Git CLI commands — those live in the GitPort adapter.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class GitOperationsNode:
    """
    Applies a validated patch to the repository via GitPort.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Git Operations step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with PR URL in ``answer``.

        Note:
            Implementation pending.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="GitOperations", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="GitOperations",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        return {}
