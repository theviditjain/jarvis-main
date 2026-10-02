"""
ExecutionPlan — Domain Model.

Describes the structured plan the Planner node produces before
retrieval and reasoning begin. The plan decides which tools to use,
in what order, and with what parameters.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PlanStepType(str, Enum):
    """Type of operation a single plan step performs."""

    GRAPH_QUERY = "GRAPH_QUERY"
    VECTOR_SEARCH = "VECTOR_SEARCH"
    REPOSITORY_READ = "REPOSITORY_READ"
    REASONING = "REASONING"
    PATCH_GENERATION = "PATCH_GENERATION"
    GIT_OPERATION = "GIT_OPERATION"
    REFLECTION = "REFLECTION"
    RESPONSE = "RESPONSE"


class PlanStep(BaseModel):
    """
    A single step in an ExecutionPlan.

    Attributes:
        step_id:     Monotonically increasing step identifier within the plan.
        step_type:   Type of operation this step performs.
        description: Human-readable description of the step's intent.
        parameters:  Arbitrary key-value pairs passed to the step handler.
        depends_on:  IDs of steps that must complete before this step runs.
    """

    step_id: int = Field(..., description="Monotonically increasing step identifier.")
    step_type: PlanStepType = Field(..., description="Type of operation.")
    description: str = Field(..., description="Human-readable step description.")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters passed to the step handler.",
    )
    depends_on: List[int] = Field(
        default_factory=list,
        description="Step IDs that must complete before this step.",
    )


class ExecutionPlan(BaseModel):
    """
    The structured plan produced by the Planner node.

    The planner analyses the user's intent and produces this plan, which
    directs all subsequent graph nodes in the LangGraph workflow. The
    plan is immutable once created — subsequent nodes may annotate it
    with results but must not mutate step definitions.

    Attributes:
        plan_id:         Unique identifier for this plan.
        execution_mode:  READ, WRITE, or HYBRID.
        steps:           Ordered list of plan steps.
        rationale:       LLM-generated explanation of why this plan was chosen.
        estimated_hops:  Estimated number of graph hops required.
        max_iterations:  Maximum reflection iterations permitted.
    """

    plan_id: str = Field(..., description="Unique identifier for this plan.")
    execution_mode: str = Field(
        ...,
        description="Execution mode: READ | WRITE | HYBRID.",
    )
    steps: List[PlanStep] = Field(
        default_factory=list,
        description="Ordered list of plan steps.",
    )
    rationale: Optional[str] = Field(
        default=None,
        description="LLM-generated explanation of the chosen plan.",
    )
    estimated_hops: int = Field(
        default=1,
        ge=1,
        description="Estimated number of graph traversal hops.",
    )
    max_iterations: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum reflection iterations.",
    )
