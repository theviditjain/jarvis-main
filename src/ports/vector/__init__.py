"""
VectorSearchPort — Abstract Vector Store Interface.

Defines the contract for Milvus vector search operations. The
application layer uses this port to find semantically similar
code elements based on query embeddings.

Milvus stores semantic knowledge about the codebase. It works in
conjunction with Neo4j: Neo4j provides structural relationships,
Milvus provides semantic similarity.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class VectorSearchPort(ABC):
    """
    Abstract port for Milvus vector store operations.

    Hybrid retrieval begins here: Milvus performs a semantic + keyword (BM25)
    search. The results are later filtered by an LLM and expanded by GraphPort.
    """

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        collection: str,
        *,
        top_k: int = 10,
        filter_expr: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform an approximate nearest-neighbour vector search.

        Args:
            query_vector:  Embedding vector for the query.
            collection:    Target Milvus collection name.
            top_k:         Number of results to return.
            filter_expr:   Optional Milvus filter expression.
            output_fields: Fields to include in the result.

        Returns:
            List of result dictionaries sorted by descending similarity.
        """
        ...

    @abstractmethod
    async def search_by_text(
        self,
        query_text: str,
        collection: str,
        *,
        top_k: int = 10,
        filter_expr: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Convenience method: embed query text then search.

        Args:
            query_text:   Raw text to embed and search with.
            collection:   Target Milvus collection name.
            top_k:        Number of results to return.
            filter_expr:  Optional Milvus filter expression.
            repository_id: Restrict search to a single repository.

        Returns:
            List of result dictionaries sorted by descending similarity.
        """
        ...

    @abstractmethod
    async def hybrid_search(
        self,
        query_text: str,
        collections: List[str],
        *,
        top_k: int = 10,
        repository_id: Optional[str] = None,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Execute a semantic + keyword (BM25) search on Milvus.

        Searches collections using dense embeddings (semantic) and sparse 
        embeddings (BM25 keyword search) merged internally.

        Args:
            query_text:    Raw text to embed and search with.
            collections:   List of Milvus collection names.
            top_k:         Number of results to return after reranking.
            repository_id: Restrict search to a single repository.
            rerank:        Apply internal reranking to merged results.

        Returns:
            Merged and reranked list of result dictionaries.
        """
        ...

    @abstractmethod
    async def get_collections(self) -> List[str]:
        """
        List all available Milvus collections.

        Returns:
            List of collection name strings.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify that the Milvus connection is healthy."""
        ...
