"""
LoggingPort — Abstract Structured Logging Interface.

Defines the contract for structured logging throughout the application.
The concrete implementation uses structlog, but the application layer
never imports structlog directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoggingPort(ABC):
    """
    Abstract port for structured logging.

    All application and domain code logs through this port. The
    structlog adapter provides the concrete implementation.
    """

    @abstractmethod
    def debug(self, event: str, **kwargs: Any) -> None:
        """Emit a DEBUG-level structured log event."""
        ...

    @abstractmethod
    def info(self, event: str, **kwargs: Any) -> None:
        """Emit an INFO-level structured log event."""
        ...

    @abstractmethod
    def warning(self, event: str, **kwargs: Any) -> None:
        """Emit a WARNING-level structured log event."""
        ...

    @abstractmethod
    def error(self, event: str, **kwargs: Any) -> None:
        """Emit an ERROR-level structured log event."""
        ...

    @abstractmethod
    def critical(self, event: str, **kwargs: Any) -> None:
        """Emit a CRITICAL-level structured log event."""
        ...

    @abstractmethod
    def bind(self, **kwargs: Any) -> "LoggingPort":
        """
        Return a new logger with the given context variables bound.

        Args:
            **kwargs: Context key-value pairs to bind.

        Returns:
            A new LoggingPort instance with the context bound.
        """
        ...


class MetricsPort(ABC):
    """
    Abstract port for metrics and observability.

    The concrete implementation may use Prometheus, OpenTelemetry, or
    any other observability backend. The application layer must not
    know which backend is in use.
    """

    @abstractmethod
    def increment(self, metric: str, value: int = 1, **tags: Any) -> None:
        """Increment a counter metric."""
        ...

    @abstractmethod
    def gauge(self, metric: str, value: float, **tags: Any) -> None:
        """Set a gauge metric to a specific value."""
        ...

    @abstractmethod
    def histogram(self, metric: str, value: float, **tags: Any) -> None:
        """Record a value in a histogram metric."""
        ...

    @abstractmethod
    def timing(self, metric: str, value_ms: float, **tags: Any) -> None:
        """Record a timing measurement in milliseconds."""
        ...
