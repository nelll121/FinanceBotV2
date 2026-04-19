"""Handlers package."""

from aiogram import Router

from .start import router as start_router


def setup_routers() -> Router:
    """Create root router with all feature routers attached."""
    root = Router(name="root")
    root.include_router(start_router)
    return root
