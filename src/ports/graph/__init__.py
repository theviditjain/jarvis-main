"""
GraphPort — Abstract Graph Database Interface.

Defines the contract for Neo4j graph traversal operations. The
application layer uses this port to discover code relationships,
traverse dependency chains, and retrieve subgraphs.

Neo4j stores relationships between code entities. It is NOT the
source of truth for source code content — repository files are.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class GraphPort(ABC):
    """
    Abstract port for Neo4j graph database operations.

    The application layer communicates with the graph exclusively through
    this port. Cypher queries live in the Neo4j adapter — not here.
    """

    @abstractmethod
    async def find_node_by_id(
        self,
        node_id: str,
        repository_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single node by its Neo4j element ID.

        Args:
            node_id:       Neo4j element ID of the target node.
            repository_id: Optional repository scope filter.

        Returns:
            A dictionary of node properties, or None if not found.
        """
        ...

    @abstractmethod
    async def find_nodes_by_name(
        self,
        name: str,
        node_types: Optional[List[str]] = None,
        repository_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find nodes whose name matches the given string.

        Args:
            name:          Name or qualified name to search for.
            node_types:    Filter to specific node types.
            repository_id: Repository scope filter.
            limit:         Maximum number of results.

        Returns:
            List of matching node property dictionaries.
        """
        ...

    @abstractmethod
    async def get_neighbours(
        self,
        node_id: str,
        relationship_types: Optional[List[str]] = None,
        depth: int = 1,
        direction: str = "BOTH",
    ) -> List[Dict[str, Any]]:
        """
        Traverse the graph to retrieve neighbouring nodes.

        Args:
            node_id:             Starting node ID.
            relationship_types:  Filter to specific relationship types.
            depth:               Maximum traversal depth.
            direction:           'IN', 'OUT', or 'BOTH'.

        Returns:
            List of neighbouring node property dictionaries.
        """
        ...

    @abstractmethod
    async def get_dependency_chain(
        self,
        node_id: str,
        repository_id: Optional[str] = None,
        max_depth: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the full dependency chain for a given node.

        Used during WRITE operations to determine which entities are
        affected by a proposed change.

        Args:
            node_id:       Root node of the dependency chain.
            repository_id: Repository scope filter.
            max_depth:     Maximum traversal depth.

        Returns:
            Ordered list of dependent node property dictionaries.
        """
        ...

    @abstractmethod
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw Cypher query (adapter implements this).

        This escape hatch exists for the adapter only. Application
        nodes should prefer the higher-level methods above.

        Args:
            query:      Cypher query string.
            parameters: Query parameter bindings.

        Returns:
            List of result record dictionaries.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify that the Neo4j connection is healthy."""
        ...
