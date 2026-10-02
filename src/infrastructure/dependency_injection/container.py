"""
Dependency Injection Container.

Wires all ports to their concrete adapter implementations.
The container is instantiated once at application startup and
injected into FastAPI routes via dependency functions.

Architecture:
  - The container owns the lifetime of all adapter instances.
  - Ports are bound to adapters here — nowhere else in the codebase.
  - Application nodes receive ports via constructor injection.
  - FastAPI routes receive use cases via FastAPI's Depends() system.
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from adapters.outbound.openai.openai_adapter import OpenAIAdapter
from adapters.outbound.neo4j.neo4j_adapter import Neo4jAdapter
from adapters.outbound.milvus.milvus_adapter import MilvusAdapter
from adapters.outbound.sse.sse_adapter import SSEAdapter
from adapters.outbound.yaml.yaml_configuration_adapter import YamlConfigurationAdapter
from adapters.outbound.bigquery.bigquery_adapter import BigQueryAdapter
from ports.llm import LLMPort
from ports.graph import GraphPort
from ports.vector import VectorSearchPort
from ports.streaming import StreamingPort
from ports.configuration import ConfigurationPort
from ports.audit import AuditPort


class Container:
    """
    Dependency Injection Container.

    Instantiates and wires all adapters. Provides accessor methods
    that return port-typed instances (the application layer only
    sees the port interface, never the concrete adapter class).

    This container uses lazy initialisation — adapters are created
    on first access to avoid slow startup during testing.
    """

    def __init__(self) -> None:
        self._config: ConfigurationPort | None = None
        self._llm: LLMPort | None = None
        self._graph: GraphPort | None = None
        self._vector: VectorSearchPort | None = None
        self._streaming: StreamingPort | None = None
        self._audit: AuditPort | None = None

    @property
    def configuration(self) -> ConfigurationPort:
        """Provide the ConfigurationPort (YamlConfigurationAdapter)."""
        if self._config is None:
            env = os.environ.get("JARVIS_ENV", "development")
            config_dir = Path(__file__).parents[3] / "configs"
            self._config = YamlConfigurationAdapter(
                config_dir=config_dir,
                environment=env,
            )
        return self._config

    @property
    def llm(self) -> LLMPort:
        """Provide the LLMPort (OpenAIAdapter)."""
        if self._llm is None:
            cfg = self.configuration
            self._llm = OpenAIAdapter(
                api_key=cfg.get_required("llm.openai.api_key"),
                model=cfg.get("llm.openai.model", "gpt-4o"),
                embedding_model=cfg.get(
                    "llm.openai.embedding_model", "text-embedding-3-large"
                ),
                timeout=float(cfg.get("llm.openai.timeout", 60.0)),
                max_retries=int(cfg.get("llm.openai.max_retries", 3)),
            )
        return self._llm

    @property
    def graph(self) -> GraphPort:
        """Provide the GraphPort (Neo4jAdapter)."""
        if self._graph is None:
            cfg = self.configuration
            self._graph = Neo4jAdapter(
                uri=cfg.get_required("database.neo4j.uri"),
                user=cfg.get_required("database.neo4j.user"),
                password=cfg.get_required("database.neo4j.password"),
                database=cfg.get("database.neo4j.database", "neo4j"),
            )
        return self._graph

    @property
    def vector(self) -> VectorSearchPort:
        """Provide the VectorSearchPort (MilvusAdapter)."""
        if self._vector is None:
            cfg = self.configuration
            self._vector = MilvusAdapter(
                uri=cfg.get_required("database.milvus.uri"),
                token=cfg.get("database.milvus.token"),
                timeout=float(cfg.get("database.milvus.timeout", 30.0)),
            )
        return self._vector

    @property
    def streaming(self) -> StreamingPort:
        """Provide the StreamingPort (SSEAdapter)."""
        if self._streaming is None:
            self._streaming = SSEAdapter(max_queue_size=1000)
        return self._streaming

    @property
    def audit(self) -> AuditPort:
        """Provide the AuditPort (BigQueryAdapter)."""
        if self._audit is None:
            db_config = self.configuration.get_config("database.bigquery")
            
            # Extract configuration, handling potential missing dictionary
            if not isinstance(db_config, dict):
                raise ValueError("database.bigquery configuration is missing or invalid")
                
            self._audit = BigQueryAdapter(
                project_id=db_config.get("project_id", ""),
                dataset_id=db_config.get("dataset_id", ""),
                table_id=db_config.get("table_id", ""),
            )
        return self._audit


@lru_cache(maxsize=1)
def get_container() -> Container:
    """
    FastAPI dependency provider for the DI container.

    Usage in route handlers:
        container: Container = Depends(get_container)
    """
    return Container()
