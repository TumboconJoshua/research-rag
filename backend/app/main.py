"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.config import get_settings
from app.utils.logger import setup_logging, get_logger
from app.utils.rate_limiter import init_rate_limiting

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    settings = get_settings()
    logger.info(
        "app_starting",
        model=settings.gemini_model,
        chroma_dir=settings.chroma_persist_dir,
    )
    yield
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ResearchRAG API",
        description="AI-powered research paper analysis, reference validation, and conversational Q&A.",
        version="1.0.0",
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.cors_origins.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_rate_limiting(app)
    app.include_router(router)

    @app.get("/health", tags=["Health"])
    async def health(request: Request):
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
