"""
ChatUseCase — Application Use Case.

Orchestrates the full chat workflow from request to SSE stream.
This use case is the primary entry point for the chat API.
"""

from __future__ import annotations

from typing import Optional

from ports.llm import LLMPort
from ports.graph import GraphPort
from ports.vector import VectorSearchPort
from ports.streaming import StreamingPort


class ChatUseCase:
    """
    Orchestrates a streaming chat request through the LangGraph workflow.

    Dependencies are injected via constructor — no direct adapter imports.

    Placeholder — implementation pending.
    """

    def __init__(
        self,
        llm: LLMPort,
        graph: GraphPort,
        vector: VectorSearchPort,
        streaming: StreamingPort,
    ) -> None:
        self._llm = llm
        self._graph = graph
        self._vector = vector
        self._streaming = streaming

    async def execute(
        self,
        query: str,
        session_id: str,
        repository_id: Optional[str] = None,
        cluster_id: Optional[str] = None,
    ) -> None:
        """
        Execute the chat workflow for a given query.

        Args:
            query:         User's natural language query.
            session_id:    Streaming session ID.
            repository_id: Optional repository scope.
            cluster_id:    Optional cluster scope for cross-repository isolation.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("ChatUseCase.execute is not yet implemented.")
