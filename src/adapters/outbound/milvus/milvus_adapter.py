"""
MilvusAdapter — Vector Search Port Implementation.

Concrete implementation of VectorSearchPort using the Milvus Python SDK.
All collection schema definitions and search configurations live here.

IMPORTANT:
  - This adapter contains ONLY infrastructure concerns.
  - Embedding generation is delegated to LLMPort (via OpenAI).
  - Reranking logic (RRF) lives here as infrastructure, not business logic.
  - No domain models constructed here — return plain dicts.

Supported Collections:
  - jarvis_methods:       Method-level embeddings.
  - jarvis_classes:       Class-level embeddings.
  - jarvis_capabilities:  Business capability embeddings.
  - jarvis_readmes:       Repository README embeddings.
  - jarvis_configs:       Configuration file embeddings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pymilvus import MilvusClient

from ports.vector import VectorSearchPort


class MilvusAdapter(VectorSearchPort):
    """
    Milvus implementation of VectorSearchPort.

    Uses the pymilvus MilvusClient (high-level API). All collection
    queries, filter expressions, and search parameters are managed here.

    Configuration keys (via ConfigurationPort):
        database.milvus.uri:      Milvus connection URI.
        database.milvus.token:    Authentication token (if required).
        database.milvus.timeout:  Request timeout in seconds.
    """

    def __init__(
        self,
        uri: str,
        token: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialise the Milvus adapter.

        Args:
            uri:     Milvus connection URI (e.g. http://localhost:19530).
            token:   Authentication token for Milvus Cloud.
            timeout: Request timeout in seconds.
        """
        self._client = MilvusClient(uri=uri, token=token)
        self._timeout = timeout

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
        Perform ANN vector search.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("MilvusAdapter.search is not yet implemented.")

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
        Embed and search by text.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("MilvusAdapter.search_by_text is not yet implemented.")

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
        Semantic + keyword (BM25) hybrid search.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("MilvusAdapter.hybrid_search is not yet implemented.")

    async def get_collections(self) -> List[str]:
        """
        List available collections.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("MilvusAdapter.get_collections is not yet implemented.")

    async def health_check(self) -> bool:
        """
        Verify Milvus connectivity.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("MilvusAdapter.health_check is not yet implemented.")
