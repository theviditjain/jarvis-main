"""
Unit tests for StreamEvent domain events.
"""

from __future__ import annotations

import json

import pytest

from domain.events.stream_event import StreamEvent, StreamEventType


class TestStreamEvent:
    def test_event_creation(self):
        event = StreamEvent(
            event_type=StreamEventType.STATUS,
            session_id="session-123",
            message="Starting workflow…",
            sequence=0,
        )
        assert event.event_type == StreamEventType.STATUS
        assert event.session_id == "session-123"

    def test_to_sse_format(self):
        event = StreamEvent(
            event_type=StreamEventType.DONE,
            session_id="session-abc",
            sequence=10,
        )
        sse = event.to_sse()
        assert sse.startswith("event: DONE\n")
        assert "data: " in sse
        assert sse.endswith("\n\n")

    def test_to_sse_data_is_valid_json(self):
        event = StreamEvent(
            event_type=StreamEventType.MARKDOWN,
            session_id="session-xyz",
            data={"chunk": "Hello world"},
            sequence=5,
        )
        sse = event.to_sse()
        data_line = [l for l in sse.split("\n") if l.startswith("data:")]
        assert len(data_line) == 1
        payload = json.loads(data_line[0][len("data: "):])
        assert payload["event_type"] == "MARKDOWN"
        assert payload["data"]["chunk"] == "Hello world"

    def test_all_event_types_exist(self):
        expected = {"STATUS", "THINKING", "MARKDOWN", "MERMAID", "TOOL", "CITATION", "ERROR", "DONE"}
        actual = {e.value for e in StreamEventType}
        assert expected == actual
