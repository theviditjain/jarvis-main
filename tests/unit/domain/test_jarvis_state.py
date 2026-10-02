"""
Unit tests for JarvisState domain model.
"""

from __future__ import annotations

import pytest

from domain.models.jarvis_state import JarvisState
from domain.value_objects.query import Query
from domain.value_objects.intent import Intent, ExecutionMode


class TestJarvisState:
    """Tests for the JarvisState Pydantic model."""

    def test_default_state_is_valid(self):
        """JarvisState with no arguments should be valid (all optional)."""
        state = JarvisState()
        assert state.iteration == 1
        assert state.need_more_context is False
        assert state.retrieved_nodes == []
        assert state.tool_results == []
        assert state.citations == []

    def test_state_with_query(self):
        """State should accept a Query value object."""
        query = Query(original="How does PaymentService work?")
        state = JarvisState(query=query)
        assert state.query.original == "How does PaymentService work?"

    def test_state_with_intent(self):
        """State should accept an Intent value object."""
        intent = Intent(execution_mode=ExecutionMode.READ, confidence=0.9)
        state = JarvisState(intent=intent)
        assert state.intent.execution_mode == ExecutionMode.READ

    def test_state_session_id(self):
        """State should store session_id."""
        state = JarvisState(session_id="test-123")
        assert state.session_id == "test-123"

    def test_state_error_field(self):
        """State should store error messages."""
        state = JarvisState(error="Something went wrong")
        assert state.error == "Something went wrong"

    def test_state_metadata(self):
        """State should accept arbitrary metadata."""
        state = JarvisState(metadata={"trace_id": "abc", "user_id": "u-123"})
        assert state.metadata["trace_id"] == "abc"
