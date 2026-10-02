"""
Domain Events.

Events that record something significant that happened in the domain.
These are immutable facts about the past.
"""

from .stream_event import StreamEvent, StreamEventType

__all__ = [
    "StreamEvent",
    "StreamEventType",
]
