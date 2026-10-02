"""
Domain Exceptions.

Strongly-typed exceptions that express failure conditions within the
domain layer. These exceptions carry no infrastructure concerns.
"""

from .base import CodeMindError, JarvisError, DomainError
from .retrieval import RetrievalError, NodeNotFoundError
from .reasoning import ReasoningError, ContextExhaustedError
from .graph import GraphTraversalError
from .vector import VectorSearchError

__all__ = [
    "CodeMindError",
    "JarvisError",
    "DomainError",
    "RetrievalError",
    "NodeNotFoundError",
    "ReasoningError",
    "ContextExhaustedError",
    "GraphTraversalError",
    "VectorSearchError",
]
