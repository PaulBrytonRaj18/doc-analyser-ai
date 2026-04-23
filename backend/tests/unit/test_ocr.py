"""Unit Tests - OCR Services"""

import numpy as np


class TestImagePreprocessor:
    """Test image preprocessing pipeline."""

    def test_preprocessor_creation(self):
        """Test preprocessor can be instantiated."""
        from app.services.ocr.preprocessor import ImagePreprocessor

        preprocessor = ImagePreprocessor()
        
        assert preprocessor is not None
        assert preprocessor.enabled is True

    def test_preprocessing_result_structure(self):
        """Test PreprocessingResult dataclass."""
        from app.services.ocr.preprocessor import PreprocessingResult

        image = np.zeros((100, 100), dtype=np.uint8)
        
        result = PreprocessingResult(
            processed_image=image,
            preprocessing_applied=["grayscale", "threshold"],
            metadata={"deskew_angle": 0},
        )

        assert result.processed_image.shape == (100, 100)
        assert len(result.preprocessing_applied) == 2
        assert "grayscale" in result.preprocessing_applied

    def test_preprocess_disabled(self):
        """Test preprocessing when disabled."""
        from app.services.ocr.preprocessor import ImagePreprocessor

        preprocessor = ImagePreprocessor()
        
        # Override enabled setting
        preprocessor.enabled = False
        
        image = np.zeros((100, 100), dtype=np.uint8)
        result = preprocessor.preprocess(image)

        assert len(result.preprocessing_applied) == 0


class TestTesseractEngine:
    """Test Tesseract OCR engine."""

    def test_engine_creation(self):
        """Test Tesseract engine can be instantiated."""
        from app.services.ocr.tesseract_engine import TesseractEngine

        engine = TesseractEngine()
        
        assert engine is not None

    def test_tesseract_result_structure(self):
        """Test TesseractResult dataclass."""
        from app.services.ocr.tesseract_engine import TesseractResult

        result = TesseractResult(
            full_text="Invoice #123",
            language_detected="en",
            overall_confidence=0.95,
            regions=[],
            low_confidence_regions=[],
        )

        assert result.full_text == "Invoice #123"
        assert result.language_detected == "en"
        assert result.overall_confidence == 0.95
        assert result.engine_used == "tesseract"


class TestOCRRouter:
    """Test OCR router."""

    def test_router_creation(self):
        """Test OCR router can be instantiated."""
        from app.services.ocr.router import OCRRouter

        router = OCRRouter()
        
        assert router is not None

    def test_ocr_response_structure(self):
        """Test OCRResponse dataclass."""
        from app.services.ocr.router import OCRResponse

        response = OCRResponse(
            full_text="Test text",
            language_detected="en",
            overall_confidence=0.9,
            regions=[{"region_id": 1, "text": "Test", "confidence": 0.9}],
            low_confidence_regions=[],
            preprocessing_applied=["grayscale"],
            engine_used="tesseract",
        )

        assert response.full_text == "Test text"
        assert response.overall_confidence == 0.9
        assert len(response.preprocessing_applied) == 1


class TestConfidenceScorer:
    """Test confidence scoring."""

    def test_scorer_creation(self):
        """Test confidence scorer can be instantiated."""
        from app.services.ocr.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()
        
        assert scorer is not None
        assert scorer.low_threshold == 0.70
        assert scorer.high_threshold == 0.90

    def test_classify_confidence(self):
        """Test confidence classification."""
        from app.services.ocr.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()

        assert scorer.classify_confidence(0.95) == "high"
        assert scorer.classify_confidence(0.80) == "medium"
        assert scorer.classify_confidence(0.50) == "low"

    def test_color_mapping(self):
        """Test confidence color mapping for UI."""
        from app.services.ocr.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()
        
        colors = scorer.get_color_mapping()
        
        assert colors["high"] == "#10B981"
        assert colors["medium"] == "#F59E0B"
        assert colors["low"] == "#F43F5E"


class TestLanguageDetector:
    """Test language detection."""

    def test_detector_creation(self):
        """Test language detector can be instantiated."""
        from app.services.ocr.language import LanguageDetector

        detector = LanguageDetector()
        
        assert detector is not None

    def test_detect_from_text(self):
        """Test language detection from text."""
        from app.services.ocr.language import LanguageDetector

        detector = LanguageDetector()

        # English text
        result = detector.detect_from_text("The quick brown fox")
        
        assert len(result) > 0
        assert result[0].language is not None

    def test_language_name(self):
        """Test getting language name."""
        from app.services.ocr.language import LanguageDetector

        detector = LanguageDetector()
        
        assert detector.get_language_name("en") == "English"
        assert detector.get_language_name("tam") == "Tamil"
        assert detector.get_language_name("hi") == "Hindi"

    def test_supported_languages(self):
        """Test getting supported languages."""
        from app.services.ocr.language import LanguageDetector

        detector = LanguageDetector()
        
        langs = detector.get_supported_languages()
        
        assert "en" in langs
        assert "tam" in langs
        assert len(langs) > 10