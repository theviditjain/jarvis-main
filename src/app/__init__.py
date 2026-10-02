"""
JARVIS Runtime FastAPI Application Entry Point.

This module creates the FastAPI application, registers all routers,
configures middleware, and performs dependency injection setup.

The application is structured as an inbound adapter in hexagonal architecture.
It knows about FastAPI but has no direct knowledge of Neo4j, Milvus, or OpenAI.
All external dependencies are injected through the DI container.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncIterator

from adapters.inbound.api.v1 import router as api_v1_router
from infrastructure.middleware.logging_middleware import LoggingMiddleware
from infrastructure.middleware.correlation_middleware import CorrelationIdMiddleware
from infrastructure.dependency_injection.container import Container

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown lifecycle events:
      - Startup:  Initialise DI container, validate connections.
      - Shutdown: Close database connections, flush telemetry.
    """
    # Startup
    logger.info("jarvis_runtime.startup", version="0.1.0")
    container = Container()
    app.state.container = container
    yield
    # Shutdown
    logger.info("jarvis_runtime.shutdown")


def create_app() -> FastAPI:
    """
    Factory function that creates and configures the FastAPI application.

    Returns:
        A configured FastAPI application instance.
    """
    app = FastAPI(
        title="JARVIS AI Runtime",
        description=(
            "AI reasoning engine for indexed code repositories. "
            "Exposes APIs for chat, retrieval, and future code modification."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ───────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure per environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(LoggingMiddleware)

    # ── Routers ──────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
