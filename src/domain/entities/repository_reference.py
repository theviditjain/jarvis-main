"""
RepositoryReference — Domain Entity.

Represents a reference to an indexed repository that CodeMind can reason
about. This entity carries only identity and metadata. It does NOT
contain source code — source code always lives in the actual repository.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RepositoryReference(BaseModel):
    """
    A lightweight reference to a repository known to the CodeMind runtime.

    The runtime does NOT own or manage repositories. This entity
    is a pointer to an externally-indexed repository, used to scope
    retrieval queries and provide provenance for citations.

    Attributes:
        repository_id: Unique identifier assigned by codemind-parser at index time.
        name:          Human-readable name (e.g. ``org/repo``).
        language:      Primary programming language detected during indexing.
        indexed_at:    Timestamp when codemind-parser last completed indexing.
        parser_version: Version of codemind-parser that produced the index.
        default_branch: Default branch of the repository.
    """

    repository_id: str = Field(
        ...,
        description="Globally unique identifier for this repository.",
    )
    name: str = Field(
        ...,
        description="Human-readable repository name (e.g. 'org/repo').",
    )
    language: Optional[str] = Field(
        default=None,
        description="Primary programming language detected during indexing.",
    )
    indexed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the last successful index operation.",
    )
    parser_version: Optional[str] = Field(
        default=None,
        description="Version of codemind-parser that produced the index.",
    )
    default_branch: str = Field(
        default="main",
        description="Default branch of the repository.",
    )

    class Config:
        frozen = True
