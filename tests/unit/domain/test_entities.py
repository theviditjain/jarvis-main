"""
Unit tests for domain entities.
"""

from __future__ import annotations

import pytest

from domain.entities.citation import Citation
from domain.entities.retrieved_node import RetrievedNode, NodeType
from domain.entities.repository_reference import RepositoryReference


class TestCitation:
    def test_citation_is_valid(self):
        citation = Citation(
            node_id="4:abc:0",
            repository_id="repo-123",
            file_path="src/PaymentService.java",
            element_name="PaymentService",
            node_type="Class",
        )
        assert citation.node_id == "4:abc:0"
        assert citation.relevance_score == 0.0

    def test_citation_is_frozen(self):
        citation = Citation(
            node_id="4:abc:0",
            repository_id="repo-123",
            file_path="src/PaymentService.java",
            element_name="PaymentService",
            node_type="Class",
        )
        with pytest.raises(Exception):
            citation.node_id = "changed"  # type: ignore[misc]


class TestRetrievedNode:
    def test_retrieved_node_is_valid(self):
        node = RetrievedNode(
            node_id="4:xyz:0",
            node_type=NodeType.CLASS,
            name="PaymentService",
            repository_id="repo-123",
        )
        assert node.node_type == NodeType.CLASS
        assert node.relevance_score == 0.0

    def test_relevance_score_bounds(self):
        with pytest.raises(Exception):
            RetrievedNode(
                node_id="x",
                node_type=NodeType.METHOD,
                name="foo",
                repository_id="r",
                relevance_score=1.5,  # Out of bounds
            )


class TestRepositoryReference:
    def test_repository_reference_is_valid(self):
        ref = RepositoryReference(
            repository_id="repo-001",
            name="org/payment-service",
        )
        assert ref.default_branch == "main"
        assert ref.language is None
