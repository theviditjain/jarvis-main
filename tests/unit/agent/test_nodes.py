"""
Unit tests for LangGraph nodes.

All tests use mock ports — no real I/O, no API keys required.
"""

from __future__ import annotations

import pytest

from agent.nodes.query_enhancement import QueryEnhancementNode
from agent.nodes.intent_classification import IntentClassificationNode
from agent.nodes.planner import PlannerNode
from agent.nodes.hybrid_retrieval import HybridRetrievalNode
from agent.nodes.context_builder import ContextBuilderNode
from agent.nodes.operation_router import OperationRouterNode
from agent.nodes.reasoning import ReasoningNode
from agent.nodes.reflection import ReflectionNode
from agent.nodes.response import ResponseNode
from agent.nodes.patch_planner import PatchPlannerNode
from agent.nodes.validation import ValidationNode


class TestQueryEnhancementNode:
    async def test_passthrough_returns_original_query(self, base_state, runnable_config):
        result = await QueryEnhancementNode.run(base_state, runnable_config)
        assert "enhanced_query" in result
        assert result["enhanced_query"] == "How does PaymentService work?"


class TestIntentClassificationNode:
    async def test_defaults_to_read_mode(self, base_state, runnable_config):
        result = await IntentClassificationNode.run(base_state, runnable_config)
        assert result["intent"]["execution_mode"] == "READ"

    async def test_returns_intent_dict(self, base_state, runnable_config):
        result = await IntentClassificationNode.run(base_state, runnable_config)
        intent = result["intent"]
        assert "execution_mode" in intent
        assert "category" in intent
        assert "confidence" in intent


class TestPlannerNode:
    async def test_returns_execution_plan(self, base_state, runnable_config):
        base_state["intent"] = {"execution_mode": "READ"}
        result = await PlannerNode.run(base_state, runnable_config)
        assert "execution_plan" in result
        plan = result["execution_plan"]
        assert plan["execution_mode"] == "READ"
        assert "plan_id" in plan

    async def test_plan_has_max_iterations(self, base_state, runnable_config):
        base_state["intent"] = {"execution_mode": "HYBRID"}
        result = await PlannerNode.run(base_state, runnable_config)
        assert result["execution_plan"]["max_iterations"] == 3


class TestHybridRetrievalNode:
    async def test_returns_empty_nodes_placeholder(self, base_state, runnable_config):
        result = await HybridRetrievalNode.run(base_state, runnable_config)
        assert result["retrieved_nodes"] == []
        assert result["tool_results"] == []


class TestContextBuilderNode:
    async def test_returns_empty_context_placeholder(self, base_state, runnable_config):
        result = await ContextBuilderNode.run(base_state, runnable_config)
        assert "context" in result
        assert "graph_context" in result


class TestOperationRouterNode:
    async def test_returns_empty_dict(self, base_state, runnable_config):
        result = await OperationRouterNode.run(base_state, runnable_config)
        assert result == {}


class TestReasoningNode:
    async def test_returns_placeholder_answer(self, base_state, runnable_config):
        result = await ReasoningNode.run(base_state, runnable_config)
        assert "answer" in result
        assert "reasoning" in result
        assert "citations" in result


class TestReflectionNode:
    async def test_increments_iteration(self, base_state, runnable_config):
        base_state["iteration"] = 1
        result = await ReflectionNode.run(base_state, runnable_config)
        assert result["iteration"] == 2

    async def test_defaults_to_done(self, base_state, runnable_config):
        result = await ReflectionNode.run(base_state, runnable_config)
        assert result["need_more_context"] is False


class TestValidationNode:
    async def test_marks_patch_as_valid(self, base_state, runnable_config):
        base_state["patch"] = {
            "patch_id": "test-patch",
            "repository_id": "repo-123",
            "branch": "jarvis/test",
            "title": "Test patch",
            "description": "Test",
            "files": [],
            "validated": False,
            "validation_errors": [],
        }
        result = await ValidationNode.run(base_state, runnable_config)
        assert result["patch"]["validated"] is True
        assert result["patch"]["validation_errors"] == []

    async def test_handles_none_patch(self, base_state, runnable_config):
        base_state["patch"] = None
        result = await ValidationNode.run(base_state, runnable_config)
        assert result == {}


class TestPatchPlannerNode:
    async def test_returns_patch_skeleton(self, base_state, runnable_config):
        result = await PatchPlannerNode.run(base_state, runnable_config)
        assert "patch" in result
        patch = result["patch"]
        assert "patch_id" in patch
        assert patch["repository_id"] == "test-repo-456"
        assert patch["validated"] is False
