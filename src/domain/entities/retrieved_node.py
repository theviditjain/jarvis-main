"""
RetrievedNode — Domain Entity.

Represents a code graph node retrieved from Neo4j or Milvus during a
hybrid retrieval pass. Carries the data needed for reasoning and citation
generation without containing the actual source file.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Mirrors the node types stored in the Neo4j graph by codemind-parser."""

    REPOSITORY = "Repository"
    MODULE = "Module"
    PACKAGE = "Package"
    CLASS = "Class"
    INTERFACE = "Interface"
    ENUM = "Enum"
    ANNOTATION = "Annotation"
    METHOD = "Method"
    CONSTRUCTOR = "Constructor"
    FIELD = "Field"
    REST_ENDPOINT = "RESTEndpoint"
    KAFKA_TOPIC = "KafkaTopic"
    DATABASE_TABLE = "DatabaseTable"
    CONFIGURATION = "Configuration"
    ENVIRONMENT_VARIABLE = "EnvironmentVariable"
    UNKNOWN = "Unknown"


class RetrievedNode(BaseModel):
    """
    A node retrieved from the graph or vector store during a retrieval pass.

    This is a read-only snapshot used by the reasoning layer. It is NOT
    a live proxy to Neo4j — it is a plain value object created from the
    query result.

    Attributes:
        node_id:        Neo4j element ID or Milvus primary key.
        node_type:      Semantic type of the node (Class, Method, …).
        name:           Qualified name of the code element.
        file_path:      Repository-relative path to the source file.
        repository_id:  Repository this node belongs to.
        language:       Programming language of the source file.
        summary:        LLM-generated or docstring-derived summary.
        relevance_score: Cosine similarity or graph traversal score.
        metadata:       Arbitrary additional metadata from the index.
    """

    node_id: str = Field(..., description="Unique node identifier.")
    node_type: NodeType = Field(..., description="Semantic type of the code element.")
    name: str = Field(..., description="Qualified name of the code element.")
    file_path: Optional[str] = Field(
        default=None,
        description="Repository-relative path to the source file.",
    )
    repository_id: str = Field(
        ..., description="Identifier of the owning repository."
    )
    language: Optional[str] = Field(
        default=None,
        description="Programming language of the source file.",
    )
    summary: Optional[str] = Field(
        default=None,
        description="Human-readable summary of this code element.",
    )
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Normalised relevance score in [0, 1].",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata from the index.",
    )

    class Config:
        frozen = True
