"""
API v1 Router.

Aggregates all v1 endpoint routers into a single APIRouter.
"""

from fastapi import APIRouter

from adapters.inbound.api.v1.chat import router as chat_router
from adapters.inbound.api.v1.retrieval import router as retrieval_router
from adapters.inbound.api.v1.health import router as health_router

router = APIRouter()
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
router.include_router(retrieval_router, prefix="/retrieval", tags=["Retrieval"])
router.include_router(health_router, prefix="/health", tags=["Health"])
