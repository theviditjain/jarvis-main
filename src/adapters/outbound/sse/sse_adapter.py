"""
SSEAdapter — Streaming Port Implementation.

Concrete implementation of StreamingPort using an in-memory asyncio
queue per session. The FastAPI SSE endpoint subscribes to the queue
and streams events to the HTTP client.

Architecture:
  Each streaming session maintains an asyncio.Queue[StreamEvent].
  The workflow emits events by putting them into the queue.
  The SSE endpoint dequeues and serialises events to the wire format.
  A DONE event signals the endpoint to close the connection.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator, Dict, Optional

from domain.events.stream_event import StreamEvent, StreamEventType
from ports.streaming import StreamingPort


class SSEAdapter(StreamingPort):
    """
    In-memory asyncio queue-based SSE streaming adapter.

    Manages per-session event queues. Thread-safe within a single
    asyncio event loop (i.e. a single FastAPI worker process).

    For multi-process or multi-worker deployments, replace with a
    Redis Pub/Sub adapter (future: RedisStreamingAdapter).
    """

    def __init__(self, max_queue_size: int = 1000) -> None:
        """
        Initialise the SSE adapter.

        Args:
            max_queue_size: Maximum events buffered per session queue.
        """
        self._queues: Dict[str, asyncio.Queue[StreamEvent]] = {}
        self._max_queue_size = max_queue_size

    def _get_or_create_queue(self, session_id: str) -> asyncio.Queue[StreamEvent]:
        """Get or create the queue for a session."""
        if session_id not in self._queues:
            self._queues[session_id] = asyncio.Queue(maxsize=self._max_queue_size)
        return self._queues[session_id]

    async def emit(self, event: StreamEvent) -> None:
        """
        Emit a StreamEvent to the session queue.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("SSEAdapter.emit is not yet implemented.")

    async def emit_status(
        self,
        session_id: str,
        message: str,
        sequence: int = 0,
    ) -> None:
        """
        Emit a STATUS event.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("SSEAdapter.emit_status is not yet implemented.")

    async def emit_thinking(
        self,
        session_id: str,
        message: str,
        sequence: int = 0,
    ) -> None:
        """
        Emit a THINKING event.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("SSEAdapter.emit_thinking is not yet implemented.")

    async def emit_markdown_chunk(
        self,
        session_id: str,
        chunk: str,
        sequence: int = 0,
    ) -> None:
        """
        Emit a MARKDOWN chunk event.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("SSEAdapter.emit_markdown_chunk is not yet implemented.")

    async def emit_done(
        self,
        session_id: str,
        sequence: int = 0,
    ) -> None:
        """
        Emit a DONE terminal event.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("SSEAdapter.emit_done is not yet implemented.")

    async def subscribe(
        self,
        session_id: str,
    ) -> AsyncIterator[StreamEvent]:
        """
        Subscribe to the event stream for a session.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("SSEAdapter.subscribe is not yet implemented.")
        # Required for async generator type annotation; never reached.
        yield StreamEvent(  # type: ignore[misc]
            event_type=StreamEventType.DONE, session_id=session_id
        )

    def teardown_session(self, session_id: str) -> None:
        """Remove a session queue after the client disconnects."""
        self._queues.pop(session_id, None)
