"""
Health Check API Endpoints — v1.

Provides liveness and readiness probes for orchestration platforms
(Kubernetes, Docker Compose, etc.).

Endpoints:
  GET /api/v1/health/live   — Liveness probe (is the process running?).
  GET /api/v1/health/ready  — Readiness probe (are all backends connected?).
  GET /api/v1/health/status — Detailed health status of all dependencies.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LivenessResponse(BaseModel):
    status: str = "ok"


class ReadinessResponse(BaseModel):
    status: str
    neo4j: bool
    milvus: bool
    openai: bool


@router.get(
    "/live",
    response_model=LivenessResponse,
    summary="Liveness probe",
    operation_id="health_live",
)
async def liveness() -> LivenessResponse:
    """
    Liveness probe — confirms the process is running.
    Always returns 200 OK if the process is alive.
    """
    return LivenessResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    operation_id="health_ready",
)
async def readiness() -> ReadinessResponse:
    """
    Readiness probe — checks connectivity to all backends.

    Returns 200 if all backends are healthy, 503 if any are unavailable.

    Placeholder — health check implementations pending.
    """
    # Placeholder: mark all as healthy pending real implementation.
    return ReadinessResponse(status="ok", neo4j=True, milvus=True, openai=True)


@router.get(
    "/status",
    summary="Detailed health status",
    operation_id="health_status",
)
async def health_status() -> dict:
    """
    Detailed health status including version and configuration summary.

    Placeholder — implementation pending.
    """
    return {
        "status": "ok",
        "version": "0.1.0",
        "backends": {
            "neo4j": "not_checked",
            "milvus": "not_checked",
            "openai": "not_checked",
        },
    }
