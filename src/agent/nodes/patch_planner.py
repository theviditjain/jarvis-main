"""
PatchPlannerNode — LangGraph Node.

PURPOSE:
  Plans the specific code modifications required to satisfy the user's
  WRITE or HYBRID request. The Patch Planner:
    - Identifies which files need to be modified, created, or deleted.
    - Uses the dependency chain from Neo4j to assess impact.
    - Produces a PatchFile list describing each required change.
    - Determines what source code must be read before generation.

POSITION IN WORKFLOW:
  WRITE:  OperationRouter → [PatchPlanner] → RepositoryReader
  HYBRID: Reflection → [PatchPlanner] → RepositoryReader

INPUTS (from JarvisState):
  - reasoning:      Reasoning output (HYBRID mode only).
  - enhanced_query: Enriched user request.
  - retrieved_nodes: Nodes with dependency information.
  - execution_plan:  Plan with write-specific parameters.

OUTPUTS (to JarvisState):
  - patch: Partially constructed Patch with planned PatchFiles.

DESIGN:
  - Calls LLMPort.complete() with a patch planning prompt.
  - Uses GraphPort to resolve impact chain (which files are affected).
  - Emits THINKING event with planned changes summary.
  - Contains NO prompt text — prompts live in application/prompts/.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class PatchPlannerNode:
    """
    Plans the code modifications required by the WRITE/HYBRID request.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Patch Planner step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with ``patch`` skeleton populated.

        Note:
            Implementation pending. Returns an empty patch skeleton.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="PatchPlanner", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="PatchPlanner",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        repository_id = state.get("repository_id") or "unknown"
        patch_skeleton = {
            "patch_id": str(uuid.uuid4()),
            "repository_id": repository_id,
            "branch": f"jarvis/patch-{uuid.uuid4().hex[:8]}",
            "title": "Placeholder patch — implementation pending.",
            "description": "",
            "files": [],
            "validated": False,
            "validation_errors": [],
        }
        return {"patch": patch_skeleton}
