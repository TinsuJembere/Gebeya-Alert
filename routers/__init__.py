"""
API routers package.
"""
from .auth import router as auth_router
from .crops import router as crops_router
from .markets import router as markets_router
from .prices import router as prices_router
from .alerts import router as alerts_router

__all__ = [
    "auth_router",
    "crops_router",
    "markets_router",
    "prices_router",
    "alerts_router",
]


