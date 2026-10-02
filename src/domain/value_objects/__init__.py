"""
Domain Value Objects.

Immutable objects defined entirely by their attributes. They carry no
identity and are interchangeable when their values are identical.
"""

from .intent import Intent, ExecutionMode
from .query import Query
from .score import RelevanceScore

__all__ = [
    "Intent",
    "ExecutionMode",
    "Query",
    "RelevanceScore",
]
