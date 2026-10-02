"""Graph traversal domain exceptions."""

from .base import CodeMindError


class GraphTraversalError(CodeMindError):
    """Raised when a Neo4j graph traversal fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="GRAPH_TRAVERSAL_ERROR")
