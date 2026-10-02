"""Reasoning domain exceptions."""

from .base import CodeMindError


class ReasoningError(CodeMindError):
    """Raised when the reasoning layer encounters an unrecoverable error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="REASONING_ERROR")


class ContextExhaustedError(ReasoningError):
    """Raised when the token budget is exhausted before reasoning completes."""

    def __init__(self) -> None:
        super().__init__("Token budget exhausted before reasoning could complete.")
