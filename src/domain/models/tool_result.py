"""
ToolResult — Domain Model.

Captures the output of a single tool call made by a LangGraph node.
Tool results are accumulated in the JarvisState and used by the
reasoning and reflection nodes to construct a final answer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """
    The result of a single tool call made during workflow execution.

    Attributes:
        tool_name:   Name of the tool (port) that was invoked.
        step_id:     Plan step ID that triggered this tool call.
        success:     True if the tool call completed without error.
        data:        Arbitrary result data from the tool.
        error:       Error message if ``success`` is False.
        latency_ms:  Wall-clock time of the tool call in milliseconds.
        called_at:   UTC timestamp of the tool invocation.
    """

    tool_name: str = Field(..., description="Name of the invoked tool.")
    step_id: Optional[int] = Field(
        default=None, description="Plan step ID that triggered this call."
    )
    success: bool = Field(default=True, description="True if the call succeeded.")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary result data from the tool.",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the call failed.",
    )
    latency_ms: Optional[float] = Field(
        default=None,
        description="Wall-clock time of the call in milliseconds.",
    )
    called_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of the tool invocation.",
    )
