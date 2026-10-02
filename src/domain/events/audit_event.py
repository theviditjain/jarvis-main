"""
AuditEvent — Domain Event.

Represents a structured audit log entry that is guaranteed to be recorded
for compliance, observability, and debugging.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """
    A single audit event for a workflow step or action.
    """

    workflow_id: str = Field(
        ..., description="Unique ID for the entire user request / workflow execution."
    )
    step_name: str = Field(..., description="The name of the node or step executing.")
    status: str = Field(
        ..., description="Status of the step (e.g., STARTED, COMPLETED, FAILED)."
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat(),
        description="ISO 8601 timestamp in UTC.",
    )
    repository_id: Optional[str] = Field(
        default=None, description="The repository being operated on, if applicable."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary structured metadata about the step execution.",
    )
    error: Optional[str] = Field(
        default=None, description="Error message if status is FAILED."
    )
