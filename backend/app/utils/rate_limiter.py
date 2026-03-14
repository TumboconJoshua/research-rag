"""Rate limiting configuration using SlowAPI."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Store limiter as a singleton
limiter = Limiter(key_func=get_remote_address)

def init_rate_limiting(app):
    """Register limiter with the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
