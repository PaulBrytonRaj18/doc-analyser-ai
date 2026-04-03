"""
Production Configuration Management.
"""

from functools import lru_cache
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = "DocuLens AI"
    app_version: str = "3.0.0"
    environment: str = "production"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Security
    api_key: str = ""
    cors_origins: list[str] = ["*"]

    # Gemini AI
    gemini_api_key: str = ""

    # Vector Database (Pinecone)
    pinecone_api_key: str = ""
    pinecone_index_name: str = "doculens-production"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # Embedding
    embedding_provider: Literal["gemini", "openai", "local"] = "gemini"
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    local_embedding_model: str = "all-MiniLM-L6-v2"

    # Redis Cache
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    celery_enabled: bool = False

    # Document Processing
    max_file_size_mb: int = 50
    supported_file_types: list[str] = ["pdf", "docx", "txt", "png", "jpg", "jpeg"]

    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    max_context_chunks: int = 10
    streaming_enabled: bool = True

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def is_authentication_enabled(self) -> bool:
        return bool(self.api_key)

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
