"""
BigQuery Adapter.

Implements the AuditPort to stream audit events into Google BigQuery.
Uses the `insert_rows_json` streaming API for immediate availability.
"""

from __future__ import annotations

import logging
from typing import Optional

from google.cloud import bigquery

from domain.events.audit_event import AuditEvent
from ports.audit import AuditPort

logger = logging.getLogger(__name__)


class BigQueryAdapter(AuditPort):
    """
    Concrete implementation of AuditPort using Google BigQuery.
    """

    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
    ) -> None:
        """
        Initialize the BigQuery client and dataset configuration.

        Args:
            project_id: GCP project ID.
            dataset_id: BigQuery dataset name.
            table_id: BigQuery table name.
        """
        self._project_id = project_id
        self._dataset_id = dataset_id
        self._table_id = table_id
        self._table_ref = f"{project_id}.{dataset_id}.{table_id}"

        # Initialize the client. This will use Application Default Credentials
        # if GOOGLE_APPLICATION_CREDENTIALS is not explicitly set.
        try:
            self._client: Optional[bigquery.Client] = bigquery.Client(project=project_id)
        except Exception as e:
            logger.warning(
                f"Failed to initialize BigQuery client. Auditing will be disabled. Error: {e}"
            )
            self._client = None

    def log_event(self, event: AuditEvent) -> None:
        """
        Stream a single AuditEvent to BigQuery.

        Args:
            event: The AuditEvent to record.
        """
        if not self._client:
            return

        # Convert Pydantic model to dict for BigQuery JSON insertion
        row_to_insert = event.model_dump()

        try:
            errors = self._client.insert_rows_json(self._table_ref, [row_to_insert])
            if errors:
                logger.error(f"Failed to insert audit event into BigQuery: {errors}")
        except Exception as e:
            # We swallow exceptions here so that auditing failures
            # do not break the critical path of the application.
            logger.error(f"Exception during BigQuery audit logging: {e}")
