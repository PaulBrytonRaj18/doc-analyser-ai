"""
Image Preprocessing Pipeline - DocuLens AI v4.0
OpenCV-based image preprocessing for OCR enhancement
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, List

from app.core.config import settings


@dataclass
class PreprocessingResult:
    processed_image: np.ndarray
    preprocessing_applied: List[str]
    metadata: dict


class ImagePreprocessor:
    """OpenCV-based image preprocessing pipeline for document images."""

    def __init__(self):
        self.enabled = settings.preprocessing_enabled
        self.max_angle = settings.deskew_max_angle

    def preprocess(
        self,
        image: np.ndarray,
        apply_grayscale: bool = True,
        apply_threshold: bool = True,
        apply_deskew: bool = True,
        apply_denoise: bool = True,
        apply_clahe: bool = True,
        apply_border_crop: bool = True,
    ) -> PreprocessingResult:
        """
        Run full preprocessing pipeline on document image.
        
        Steps:
        1. Grayscale conversion
        2. Adaptive thresholding
        3. Deskew (Hough Line Transform)
        4. Denoising (FastNlMeansDenoising)
        5. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        6. Border cropping
        """
        if not self.enabled:
            return PreprocessingResult(
                processed_image=image,
                preprocessing_applied=[],
                metadata={},
            )

        processed = image.copy()
        applied_steps = []
        metadata = {}

        # 1. Grayscale conversion
        if apply_grayscale and len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            applied_steps.append("grayscale")

        # 2. Adaptive thresholding
        if apply_threshold and len(processed.shape) == 2:
            processed = self._apply_adaptive_threshold(processed)
            applied_steps.append("threshold")

        # 3. Deskew
        if apply_deskew and len(processed.shape) == 2:
            angle = self._detect_skew_angle(processed)
            if angle is not None and abs(angle) > 0.5:
                processed = self._deskew_image(processed, angle)
                applied_steps.append("deskew")
                metadata["deskew_angle"] = angle

        # 4. Denoising
        if apply_denoise and len(processed.shape) == 2:
            processed = self._apply_denoising(processed)
            applied_steps.append("denoise")

        # 5. CLAHE
        if apply_clahe and len(processed.shape) == 2:
            processed = self._apply_clahe(processed)
            applied_steps.append("clahe")

        # 6. Border cropping
        if apply_border_crop and len(processed.shape) == 2:
            processed = self._crop_borders(processed)
            applied_steps.append("border_crop")

        return PreprocessingResult(
            processed_image=processed,
            preprocessing_applied=applied_steps,
            metadata=metadata,
        )

    def _apply_adaptive_threshold(
        self, image: np.ndarray
    ) -> np.ndarray:
        """Apply adaptive thresholding to handle uneven lighting."""
        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2,
        )

    def _detect_skew_angle(self, image: np.ndarray) -> Optional[float]:
        """Detect skew angle using Hough Line Transform."""
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        lines = cv2.HoughLines(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=100,
            maxLineGap=10,
        )

        if lines is None or len(lines) == 0:
            return None

        angles = []
        for line in lines[:50]:
            rho, theta = line[0]
            angle = np.degrees(theta) - 90
            if -self.max_angle <= angle <= self.max_angle:
                angles.append(angle)

        if not angles:
            return None

        return float(np.median(angles))

    def _deskew_image(
        self, image: np.ndarray, angle: float
    ) -> np.ndarray:
        """Rotate image to correct skew."""
        height, width = image.shape
        center = (width // 2, height // 2)
        
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        return cv2.warpAffine(
            image,
            matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )

    def _apply_denoising(self, image: np.ndarray) -> np.ndarray:
        """Apply FastNlMeansDenoising for edge preservation."""
        return cv2.fastNlMeansDenoising(
            image,
            h=10,
            templateWindowSize=7,
            searchWindowSize=21,
        )

    def _apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """Apply CLAHE for contrast enhancement."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)

    def _crop_borders(self, image: np.ndarray) -> np.ndarray:
        """Remove noise borders from scanned documents."""
        h, w = image.shape
        
        # Find non-white regions
        _, binary = cv2.threshold(image, 250, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return image

        # Get largest contour
        largest = max(contours, key=cv2.contourArea)
        x, y, cw, ch = cv2.boundingRect(largest)

        # Add small margin
        margin = 5
        x = max(0, x - margin)
        y = max(0, y - margin)
        cw = min(w - x, cw + 2 * margin)
        ch = min(h - y, ch + 2 * margin)

        return image[y : y + ch, x : x + cw]

    def enhance_for_ocr(
        self, image: np.ndarray
    ) -> PreprocessingResult:
        """Quick enhancement optimized for OCR."""
        return self.preprocess(
            image,
            apply_grayscale=True,
            apply_threshold=True,
            apply_deskew=True,
            apply_denoise=True,
            apply_clahe=True,
            apply_border_crop=True,
        )

    def get_preview_overlay(
        self,
        original: np.ndarray,
        processed: np.ndarray,
    ) -> np.ndarray:
        """Generate overlay showing preprocessing regions."""
        if len(original.shape) == 2:
            original = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
        if len(processed.shape) == 2:
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)

        h, w = original.shape[:2]
        processed = cv2.resize(processed, (w, h))

        return np.hstack([original, processed])