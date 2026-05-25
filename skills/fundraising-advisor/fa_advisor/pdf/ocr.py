"""
OCR Service - Optical Character Recognition for scanned PDFs
"""

import logging
from pathlib import Path
from typing import Optional, List
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

from fa_advisor.types.models import PDFExtractionResult

logger = logging.getLogger(__name__)


class OCRService:
    """
    OCR service using Tesseract

    Capabilities:
    - Convert PDF pages to images
    - Extract text from scanned documents
    - Support for multiple languages
    - Image preprocessing
    """

    def __init__(self, language: str = 'eng+chi_sim'):
        """
        Initialize OCR service

        Args:
            language: Tesseract language codes (e.g., 'eng', 'chi_sim', 'eng+chi_sim')
        """
        self.language = language

    async def ocr_pdf(
        self,
        pdf_path: str | Path,
        dpi: int = 300,
        preprocess: bool = True
    ) -> PDFExtractionResult:
        """
        Perform OCR on a PDF file

        Args:
            pdf_path: Path to PDF file
            dpi: DPI for PDF to image conversion (higher = better quality)
            preprocess: Whether to preprocess images before OCR

        Returns:
            PDFExtractionResult with extracted text
        """
        try:
            pdf_path = Path(pdf_path)

            if not pdf_path.exists():
                return PDFExtractionResult(
                    success=False,
                    error=f"PDF file not found: {pdf_path}"
                )

            # Convert PDF to images
            images = convert_from_path(str(pdf_path), dpi=dpi)

            # Perform OCR on each page
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i + 1}/{len(images)}")

                if preprocess:
                    image = self._preprocess_image(image)

                # Extract text
                page_text = pytesseract.image_to_string(
                    image,
                    lang=self.language
                )

                if page_text.strip():
                    text_parts.append(f"--- Page {i + 1} ---\n{page_text}")

            full_text = "\n\n".join(text_parts)

            return PDFExtractionResult(
                success=True,
                text=full_text
            )

        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return PDFExtractionResult(
                success=False,
                error=str(e)
            )

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results

        - Convert to grayscale
        - Increase contrast
        - Remove noise
        """
        from PIL import ImageEnhance, ImageFilter

        # Convert to grayscale
        image = image.convert('L')

        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)

        return image

    def ocr_image(
        self,
        image_path: str | Path,
        preprocess: bool = True
    ) -> Optional[str]:
        """
        Perform OCR on a single image file

        Args:
            image_path: Path to image file
            preprocess: Whether to preprocess image

        Returns:
            Extracted text or None if failed
        """
        try:
            image = Image.open(image_path)

            if preprocess:
                image = self._preprocess_image(image)

            text = pytesseract.image_to_string(image, lang=self.language)
            return text.strip()

        except Exception as e:
            logger.error(f"Error performing OCR on image: {e}")
            return None

    def get_available_languages(self) -> List[str]:
        """Get list of available Tesseract languages"""
        try:
            return pytesseract.get_languages()
        except Exception as e:
            logger.error(f"Error getting languages: {e}")
            return []
