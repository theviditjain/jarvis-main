"""
StreamEvent — Domain Event.

Represents a single SSE (Server-Sent Events) event emitted to the
client during a streaming workflow execution. Events are the only
mechanism by which the runtime communicates progress and results
to the frontend.

Design Principle:
  - THINKING events carry high-level progress summaries only.
  - Chain-of-thought and internal reasoning are NEVER exposed.
  - MARKDOWN events carry partial or complete response content.
  - CITATION events carry individual citations as they are resolved.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class StreamEventType(str, Enum):
    """
    Supported SSE event types emitted by the CodeMind runtime.

    Attributes:
        STATUS:   Workflow lifecycle update (e.g. 'Starting retrieval…').
        THINKING: High-level reasoning progress summary (never chain-of-thought).
        MARKDOWN: Partial or complete markdown response chunk.
        MERMAID:  Mermaid diagram string for rendering.
        TOOL:     Tool invocation event (name + status).
        CITATION: A single resolved source citation.
        ERROR:    An error that occurred during processing.
        DONE:     Terminal event signalling end of stream.
    """

    STATUS = "STATUS"
    THINKING = "THINKING"
    MARKDOWN = "MARKDOWN"
    MERMAID = "MERMAID"
    TOOL = "TOOL"
    CITATION = "CITATION"
    ERROR = "ERROR"
    DONE = "DONE"


class StreamEvent(BaseModel):
    """
    A single SSE event emitted during a workflow execution.

    The client subscribes to the SSE stream and renders events
    incrementally. The stream is terminated by a DONE event.

    Attributes:
        event_type:  Type of the event.
        session_id:  Streaming session this event belongs to.
        data:        Arbitrary payload data for the event.
        message:     Human-readable message for STATUS and THINKING events.
        sequence:    Monotonically increasing sequence number within the stream.
        emitted_at:  UTC timestamp of event emission.
    """

    event_type: StreamEventType = Field(..., description="SSE event type.")
    session_id: str = Field(..., description="Streaming session identifier.")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary event payload.",
    )
    message: Optional[str] = Field(
        default=None,
        description="Human-readable message for STATUS / THINKING events.",
    )
    sequence: int = Field(
        default=0,
        ge=0,
        description="Monotonically increasing sequence number.",
    )
    emitted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of event emission.",
    )

    def to_sse(self) -> str:
        """
        Serialize this event to the SSE wire format.

        Returns:
            A string in ``event: <type>\\ndata: <json>\\n\\n`` format.
        """
        import json

        payload = self.model_dump(mode="json")
        return f"event: {self.event_type.value}\ndata: {json.dumps(payload)}\n\n"
