"""
JARVIS Runtime — Application Entry Point.

This module is the ASGI entry point for Uvicorn / Gunicorn.

Layout:
  - Source code lives in src/
  - PYTHONPATH=src is set so imports resolve without a src. prefix
  - Uvicorn entry point: main:app

Usage:
    PYTHONPATH=src uvicorn main:app --host 0.0.0.0 --port 8000
    # or via make:
    make dev
"""

from __future__ import annotations

from infrastructure.telemetry import configure_logging

# Configure structured logging before importing the FastAPI app
configure_logging(log_level="INFO", json_logs=False)

from app import app  # noqa: E402 — must be after configure_logging

__all__ = ["app"]
