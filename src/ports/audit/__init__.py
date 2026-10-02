"""
AuditPort — Abstract Auditing Interface.

Defines the contract for recording compliance and observability audit logs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.events.audit_event import AuditEvent


class AuditPort(ABC):
    """
    Abstract port for structured auditing.

    The application layer uses this to emit audit events. The concrete
    adapter (e.g., BigQueryAdapter) handles pushing these events to
    the permanent storage backend.
    """

    @abstractmethod
    def log_event(self, event: AuditEvent) -> None:
        """
        Record a single structured audit event.

        Args:
            event: The fully populated AuditEvent.
        """
        ...
