"""Unit Tests - Config Settings"""

import os
from unittest.mock import patch, MagicMock


class TestConfigSettings:
    """Test configuration settings."""

    def test_default_values(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.core.config.Settings") as mock_settings:
                mock_settings.return_value = MagicMock(
                    app_name="DocuLens AI",
                    app_version="4.0.0",
                    environment="production",
                    database_url="postgresql+asyncpg://user:pass@localhost:5432/doculens",
                    max_file_size_mb=100,
                    batch_max_files=50,
                    ocr_engine="auto",
                    chunk_size=800,
                    chunk_overlap=150,
                    top_k_results=6,
                    min_relevance_score=0.65,
                    rerank_enabled=True,
                    celery_enabled=True,
                    audit_log_enabled=True,
                    pii_detection_enabled=True,
                )
                from app.core.config import Settings
                settings = Settings()

                assert settings.app_name == "DocuLens AI"
                assert settings.app_version == "4.0.0"
                assert settings.max_file_size_mb == 100
                assert settings.batch_max_files == 50

    def test_version_property(self):
        """Test app version property."""
        from app.core.config import Settings
        settings = Settings()
        
        settings.environment = "production"
        assert settings.is_production is True
        assert settings.is_development is False

        settings.environment = "development"
        assert settings.is_production is False
        assert settings.is_development is True

    def test_authentication_property(self):
        """Test authentication property."""
        from app.core.config import Settings
        settings = Settings()
        
        settings.api_key = ""
        assert settings.is_authentication_enabled is False
        
        settings.api_key = "test-key"
        assert settings.is_authentication_enabled is True

    def test_max_file_size_bytes(self):
        """Test max file size in bytes."""
        from app.core.config import Settings
        settings = Settings()
        settings.max_file_size_mb = 100
        
        assert settings.max_file_size_bytes == 100 * 1024 * 1024

    def test_ocr_settings(self):
        """Test OCR configuration settings."""
        from app.core.config import Settings
        settings = Settings()
        
        assert settings.ocr_engine in ["auto", "tesseract", "easyocr"]
        assert settings.ocr_default_language == "eng"
        assert settings.ocr_confidence_threshold == 0.70
        assert settings.preprocessing_enabled is True
        assert settings.deskew_max_angle == 45

    def test_rag_settings(self):
        """Test RAG configuration settings."""
        import os
        
        # Set environment variables for test
        os.environ["CHUNK_SIZE"] = "800"
        os.environ["CHUNK_OVERLAP"] = "150"
        os.environ["TOP_K_RESULTS"] = "6"
        os.environ["MIN_RELEVANCE_SCORE"] = "0.65"
        os.environ["RERANK_ENABLED"] = "true"
        
        # Clear settings cache and reload
        from app.core.config import get_settings
        get_settings.cache_clear()
        settings = get_settings()
        
        assert settings.chunk_size == 800
        assert settings.chunk_overlap == 150
        assert settings.top_k_results == 6
        assert settings.min_relevance_score == 0.65
        assert settings.rerank_enabled is True