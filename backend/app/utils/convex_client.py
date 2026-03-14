"""Convex client utility."""
from convex import ConvexClient
from app.config import get_settings

def get_convex_client() -> ConvexClient:
    settings = get_settings()
    if not settings.convex_url:
        raise ValueError("CONVEX_URL is not set")
    return ConvexClient(settings.convex_url)
