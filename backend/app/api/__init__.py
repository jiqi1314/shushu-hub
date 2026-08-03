"""REST API package."""

from fastapi import APIRouter

from app.api import compare, divination, health, systems

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(systems.router, tags=["systems"])
api_router.include_router(divination.router, tags=["divination"])
api_router.include_router(compare.router, tags=["compare"])

__all__ = ["api_router"]
