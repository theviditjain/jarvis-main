"""
StreamingPort — Abstract SSE Streaming Interface.

Defines the contract for emitting Server-Sent Events to a connected
client. The streaming layer is the only output channel the application
layer uses to communicate progress and results.

All events conform to the StreamEvent domain model. The application
layer emits domain events — the adapter serialises them to SSE wire format.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from domain.events.stream_event import StreamEvent, StreamEventType


class StreamingPort(ABC):
    """
    Abstract port for SSE event streaming.

    Used by every node in the LangGraph workflow to emit progress
    and result events to the client. The workflow never writes directly
    to an HTTP response — it emits through this port.
    """

    @abstractmethod
    async def emit(self, event: StreamEvent) -> None:
        """
        Emit a single event to the connected client.

        Args:
            event: The StreamEvent to emit.

        Raises:
            StreamingError: If the client has disconnected.
        """
        ...

    @abstractmethod
    async def emit_status(
        self,
        session_id: str,
        message: str,
        sequence: int = 0,
    ) -> None:
        """
        Convenience method to emit a STATUS event.

        Args:
            session_id: The active streaming session.
            message:    Human-readable status message.
            sequence:   Event sequence number.
        """
        ...

    @abstractmethod
    async def emit_thinking(
        self,
        session_id: str,
        message: str,
        sequence: int = 0,
    ) -> None:
        """
        Emit a THINKING event with a high-level progress summary.

        IMPORTANT: Never include chain-of-thought or internal reasoning.
        Only emit human-friendly summaries of what the system is doing.

        Args:
            session_id: The active streaming session.
            message:    High-level progress summary.
            sequence:   Event sequence number.
        """
        ...

    @abstractmethod
    async def emit_markdown_chunk(
        self,
        session_id: str,
        chunk: str,
        sequence: int = 0,
    ) -> None:
        """
        Emit a MARKDOWN event containing a partial response chunk.

        Args:
            session_id: The active streaming session.
            chunk:      Markdown content chunk.
            sequence:   Event sequence number.
        """
        ...

    @abstractmethod
    async def emit_done(
        self,
        session_id: str,
        sequence: int = 0,
    ) -> None:
        """
        Emit a DONE event to signal end of stream.

        After this event, the client should close the SSE connection.

        Args:
            session_id: The active streaming session.
            sequence:   Event sequence number.
        """
        ...

    @abstractmethod
    async def subscribe(
        self,
        session_id: str,
    ) -> AsyncIterator[StreamEvent]:
        """
        Subscribe to the event stream for a given session.

        Used by the SSE endpoint to forward events to the HTTP client.

        Args:
            session_id: Session to subscribe to.

        Yields:
            StreamEvent objects as they are emitted.
        """
        ...
