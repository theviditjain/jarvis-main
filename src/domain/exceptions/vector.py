"""Vector search domain exceptions."""

from .base import CodeMindError


class VectorSearchError(CodeMindError):
    """Raised when a Milvus vector search fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="VECTOR_SEARCH_ERROR")
