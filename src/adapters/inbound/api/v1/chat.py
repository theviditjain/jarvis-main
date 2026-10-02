"""
Chat API Endpoints — v1.

Provides the primary chat interface for the JARVIS runtime.
Supports streaming via Server-Sent Events.

Endpoints:
  POST /api/v1/chat/stream    — Initiate a streaming chat session.
  GET  /api/v1/chat/stream/{session_id} — Subscribe to an SSE stream.
  POST /api/v1/chat/complete  — Non-streaming chat completion.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter()


# ── Request / Response Models ────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request body for a chat completion."""

    query: str = Field(..., min_length=1, description="User's natural language query.")
    cluster_id: Optional[str] = Field(
        default=None,
        description="Optional cluster scope (queries all clusters if omitted).",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Existing session ID to continue. Generated if not provided.",
    )
    stream: bool = Field(
        default=True,
        description="If True, returns an SSE stream. If False, waits for completion.",
    )


class ChatSessionResponse(BaseModel):
    """Response body for session initiation."""

    session_id: str = Field(..., description="Session ID for the SSE subscription.")
    stream_url: str = Field(..., description="URL to subscribe to the SSE stream.")


# ── Endpoints ────────────────────────────────────────────────────────────

@router.post(
    "/stream",
    response_model=ChatSessionResponse,
    summary="Initiate a streaming chat session",
    operation_id="chat_stream_initiate",
)
async def initiate_chat_stream(
    request: ChatRequest,
) -> ChatSessionResponse:
    """
    Initiate a JARVIS chat session and return the SSE stream URL.

    The client should then subscribe to ``GET /stream/{session_id}``
    to receive Server-Sent Events as the workflow executes.

    Placeholder — implementation pending.
    """
    session_id = request.session_id or str(uuid.uuid4())
    return ChatSessionResponse(
        session_id=session_id,
        stream_url=f"/api/v1/chat/stream/{session_id}",
    )


@router.get(
    "/stream/{session_id}",
    summary="Subscribe to an SSE event stream",
    operation_id="chat_stream_subscribe",
)
async def subscribe_to_stream(
    session_id: str,
) -> StreamingResponse:
    """
    Subscribe to a JARVIS SSE event stream.

    Returns a text/event-stream response. Events are emitted as the
    LangGraph workflow executes and must be consumed incrementally.

    Placeholder — implementation pending.
    """
    raise HTTPException(status_code=501, detail="SSE streaming not yet implemented.")


@router.post(
    "/complete",
    summary="Non-streaming chat completion",
    operation_id="chat_complete",
)
async def chat_complete(
    request: ChatRequest,
) -> dict:
    """
    Blocking chat completion — waits for the full answer before returning.

    Suitable for simple integrations that do not support SSE streaming.

    Placeholder — implementation pending.
    """
    raise HTTPException(status_code=501, detail="Blocking completion not yet implemented.")
