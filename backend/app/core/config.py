"""
Production Configuration Management - DocuLens AI v4.0
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
    app_version: str = "4.0.0"
    environment: str = "production"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Security
    api_key: str = "dev-key"
    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Database (PostgreSQL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/doculens"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Gemini AI
    gemini_api_key: str = ""
    gemini_api_key_env: str = ""
    gemini_model: str = "gemini-1.5-pro"

    # Vector Database (Pinecone)
    pinecone_api_key: str = ""
    pinecone_index_name: str = "doculens-vectors"
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
    celery_enabled: bool = True

    # Document Processing
    max_file_size_mb: int = 100
    batch_max_files: int = 50
    supported_file_types: list[str] = [
        "pdf", "docx", "txt", "png", "jpg", "jpeg", "tiff", "webp", "heic", "bmp"
    ]

    # OCR Configuration
    ocr_engine: Literal["auto", "tesseract", "easyocr"] = "auto"
    ocr_default_language: str = "eng"
    ocr_confidence_threshold: float = 0.70
    preprocessing_enabled: bool = True
    deskew_max_angle: int = 45

    # RAG Configuration
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k_results: int = 6
    max_context_chunks: int = 10
    min_relevance_score: float = 0.65
    rerank_enabled: bool = True
    streaming_enabled: bool = True

    # Rate Limiting
    rate_limit_requests: int = 200
    rate_limit_window_seconds: int = 60

    # Webhooks
    webhook_secret: str = "change-me-webhook-secret"
    webhook_retry_attempts: int = 3

    # PII & Security
    pii_detection_enabled: bool = True
    audit_log_enabled: bool = True

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


def cache_clear() -> None:
    get_settings.cache_clear()


settings = get_settings()