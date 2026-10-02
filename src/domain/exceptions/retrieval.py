"""Retrieval domain exceptions."""

from .base import CodeMindError


class RetrievalError(CodeMindError):
    """Raised when retrieval from Neo4j or Milvus fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="RETRIEVAL_ERROR")


class NodeNotFoundError(RetrievalError):
    """Raised when a specific node cannot be found in the graph."""

    def __init__(self, node_id: str) -> None:
        super().__init__(f"Node not found: {node_id!r}")
        self.node_id = node_id
