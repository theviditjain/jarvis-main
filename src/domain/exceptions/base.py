"""Base domain exceptions."""

from __future__ import annotations


class CodeMindError(Exception):
    """Root exception for all CodeMind runtime errors."""

    def __init__(self, message: str, code: str = "CODEMIND_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


# Backward compatibility alias
JarvisError = CodeMindError


class DomainError(CodeMindError):
    """Raised when a domain invariant is violated."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="DOMAIN_ERROR")
