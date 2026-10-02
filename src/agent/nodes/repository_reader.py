"""
RepositoryReaderNode — LangGraph Node.

PURPOSE:
  Reads the current source code of files that will be modified by the
  WRITE/HYBRID workflow. This node ensures the Patch Generator has
  access to the exact current state of every affected file before
  generating any diffs.

  Repository files are ALWAYS the source of truth. This node reads
  those files — it never constructs the current state from Neo4j.

POSITION IN WORKFLOW:
  PatchPlanner → [RepositoryReader] → PatchGenerator

INPUTS (from JarvisState):
  - patch:           Patch skeleton with planned PatchFiles.
  - repository_id:   Target repository.
  - execution_plan:  Plan with ref/branch parameters.

OUTPUTS (to JarvisState):
  - repository_context: Concatenated file content string for all affected files.
  - tool_results:       ToolResult records for each file read.

DESIGN:
  - Calls RepositoryReaderPort.read_files() for all affected file paths.
  - Emits TOOL events for each file read.
  - Emits THINKING event with files being read.
  - Contains NO file system access — that is in RepositoryReaderPort adapter.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from domain.events.audit_event import AuditEvent
from domain.state.graph_state import GraphStateAnnotation


class RepositoryReaderNode:
    """
    Reads source files required for patch generation.
    """

    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Repository Reader step.

        Args:
            state: Current LangGraph state.

        Returns:
            Partial state update with ``repository_context``.

        Note:
            Implementation pending. Returns empty repository context.
        """
        container = config["configurable"]["container"]
        logger = container.logging.bind(step="RepositoryReader", workflow_id=state.get("session_id", "unknown"))
        audit = container.audit
        
        logger.info("Step started")
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="RepositoryReader",
            status="STARTED",
            repository_id=state.get("repository_id")
        ))
        
        return {
            "repository_context": "",
            "tool_results": [],
        }
