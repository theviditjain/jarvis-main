"""
Shared Pytest Fixtures.

Provides reusable test fixtures for mock ports, test state objects,
and common test utilities. Import via conftest.py auto-discovery.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.events.stream_event import StreamEvent, StreamEventType
from domain.models.jarvis_state import JarvisState
from domain.value_objects.intent import ExecutionMode, Intent
from domain.value_objects.query import Query
from ports.llm import LLMPort
from ports.graph import GraphPort
from ports.vector import VectorSearchPort
from ports.streaming import StreamingPort


# ── Mock Port Implementations ────────────────────────────────────────────────

class MockLLMPort(LLMPort):
    """Mock LLM port for unit testing. Returns configurable responses."""

    def __init__(self, completion_response: str = "Mock response.") -> None:
        self._completion_response = completion_response
        self.calls: List[Dict[str, Any]] = []

    async def complete(self, system_prompt, user_prompt, **kwargs) -> str:
        self.calls.append({"method": "complete", "user_prompt": user_prompt})
        return self._completion_response

    async def stream(self, system_prompt, user_prompt, **kwargs) -> AsyncIterator[str]:
        self.calls.append({"method": "stream", "user_prompt": user_prompt})
        for word in self._completion_response.split():
            yield word + " "

    async def embed(self, texts, **kwargs) -> List[List[float]]:
        self.calls.append({"method": "embed", "count": len(texts)})
        return [[0.0] * 3072 for _ in texts]

    async def health_check(self) -> bool:
        return True


class MockGraphPort(GraphPort):
    """Mock graph port for unit testing."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    async def find_node_by_id(self, node_id, repository_id=None):
        self.calls.append({"method": "find_node_by_id", "node_id": node_id})
        return None

    async def find_nodes_by_name(self, name, node_types=None, repository_id=None, limit=10):
        self.calls.append({"method": "find_nodes_by_name", "name": name})
        return []

    async def get_neighbours(self, node_id, relationship_types=None, depth=1, direction="BOTH"):
        self.calls.append({"method": "get_neighbours", "node_id": node_id})
        return []

    async def get_dependency_chain(self, node_id, repository_id=None, max_depth=5):
        self.calls.append({"method": "get_dependency_chain", "node_id": node_id})
        return []

    async def execute_query(self, query, parameters=None):
        self.calls.append({"method": "execute_query", "query": query})
        return []

    async def health_check(self) -> bool:
        return True


class MockVectorSearchPort(VectorSearchPort):
    """Mock vector search port for unit testing."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    async def search(self, query_vector, collection, **kwargs):
        self.calls.append({"method": "search", "collection": collection})
        return []

    async def search_by_text(self, query_text, collection, **kwargs):
        self.calls.append({"method": "search_by_text", "text": query_text})
        return []

    async def hybrid_search(self, query_text, collections, **kwargs):
        self.calls.append({"method": "hybrid_search", "collections": collections})
        return []

    async def get_collections(self):
        return []

    async def health_check(self) -> bool:
        return True


class MockStreamingPort(StreamingPort):
    """Mock streaming port that records all emitted events."""

    def __init__(self) -> None:
        self.emitted_events: List[StreamEvent] = []

    async def emit(self, event: StreamEvent) -> None:
        self.emitted_events.append(event)

    async def emit_status(self, session_id, message, sequence=0) -> None:
        event = StreamEvent(
            event_type=StreamEventType.STATUS,
            session_id=session_id,
            message=message,
            sequence=sequence,
        )
        self.emitted_events.append(event)

    async def emit_thinking(self, session_id, message, sequence=0) -> None:
        event = StreamEvent(
            event_type=StreamEventType.THINKING,
            session_id=session_id,
            message=message,
            sequence=sequence,
        )
        self.emitted_events.append(event)

    async def emit_markdown_chunk(self, session_id, chunk, sequence=0) -> None:
        event = StreamEvent(
            event_type=StreamEventType.MARKDOWN,
            session_id=session_id,
            data={"chunk": chunk},
            sequence=sequence,
        )
        self.emitted_events.append(event)

    async def emit_done(self, session_id, sequence=0) -> None:
        event = StreamEvent(
            event_type=StreamEventType.DONE,
            session_id=session_id,
            sequence=sequence,
        )
        self.emitted_events.append(event)

    async def subscribe(self, session_id) -> AsyncIterator[StreamEvent]:
        for event in self.emitted_events:
            yield event

    def events_of_type(self, event_type: StreamEventType) -> List[StreamEvent]:
        return [e for e in self.emitted_events if e.event_type == event_type]


# ── Pytest Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def mock_llm() -> MockLLMPort:
    return MockLLMPort()


@pytest.fixture
def mock_graph() -> MockGraphPort:
    return MockGraphPort()


@pytest.fixture
def mock_vector() -> MockVectorSearchPort:
    return MockVectorSearchPort()


@pytest.fixture
def mock_streaming() -> MockStreamingPort:
    return MockStreamingPort()


@pytest.fixture
def base_state() -> Dict[str, Any]:
    """A minimal valid JarvisState dictionary for testing."""
    return {
        "session_id": "test-session-123",
        "repository_id": "test-repo-456",
        "query": {
            "original": "How does PaymentService work?",
            "enhanced": "",
            "language": "",
        },
        "enhanced_query": "",
        "intent": None,
        "execution_plan": None,
        "retrieved_nodes": [],
        "tool_results": [],
        "citations": [],
        "need_more_context": False,
        "iteration": 1,
        "metadata": {},
    }


@pytest.fixture
def read_intent() -> Dict[str, Any]:
    """A READ-mode intent dictionary for testing."""
    return {
        "execution_mode": "READ",
        "category": "explain",
        "confidence": 0.95,
        "entities": ["PaymentService"],
        "rationale": "User is asking an explanatory question.",
    }


@pytest.fixture
def write_intent() -> Dict[str, Any]:
    """A WRITE-mode intent dictionary for testing."""
    return {
        "execution_mode": "WRITE",
        "category": "implement",
        "confidence": 0.88,
        "entities": ["PaymentController"],
        "rationale": "User is requesting a code modification.",
    }
