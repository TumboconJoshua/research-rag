"""Application configuration using Pydantic BaseSettings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/gemini-embedding-001"

    # Convex
    convex_url: str = ""
    convex_deploy_key: str = ""

    # Storage
    chroma_persist_dir: str = "./storage"
    chroma_collection_name: str = "research_chunks"

    # Upload
    max_upload_size_mb: int = 20

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_retrieval: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
