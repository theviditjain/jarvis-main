"""
Retrieval API Endpoints — v1.

Provides direct access to the hybrid retrieval layer without
triggering the full reasoning workflow. Useful for debugging,
evaluation, and building custom frontends.

Endpoints:
  POST /api/v1/retrieval/search   — Hybrid retrieval query.
  GET  /api/v1/retrieval/node/{node_id} — Retrieve a specific graph node.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

router = APIRouter()


class RetrievalRequest(BaseModel):
    """Request body for a hybrid retrieval query."""

    query: str = Field(..., description="Search query text.")
    repository_id: Optional[str] = Field(
        default=None, description="Optional repository scope."
    )
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results.")
    collections: Optional[List[str]] = Field(
        default=None, description="Milvus collections to search."
    )
    include_graph: bool = Field(
        default=True,
        description="Include Neo4j graph traversal results.",
    )
    include_vector: bool = Field(
        default=True,
        description="Include Milvus vector search results.",
    )


@router.post(
    "/search",
    summary="Execute a hybrid retrieval query",
    operation_id="retrieval_search",
)
async def retrieval_search(
    request: RetrievalRequest,
) -> dict:
    """
    Execute a hybrid (Neo4j + Milvus) retrieval query.

    Returns merged and reranked results without LLM reasoning.

    Placeholder — implementation pending.
    """
    raise HTTPException(status_code=501, detail="Hybrid retrieval not yet implemented.")


@router.get(
    "/node/{node_id}",
    summary="Retrieve a specific graph node",
    operation_id="retrieval_node",
)
async def get_node(
    node_id: str = Path(..., description="Neo4j element ID of the target node."),
    repository_id: Optional[str] = Query(default=None),
) -> dict:
    """
    Retrieve a specific node from the Neo4j graph by element ID.

    Placeholder — implementation pending.
    """
    raise HTTPException(status_code=501, detail="Node retrieval not yet implemented.")
