"""
PDF OCR Module - Handles scanned PDFs by converting to images and extracting text.
"""

import os
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

try:
    from pdfminer.high_level import extract_text
    from pdf2image import convert_from_path
    import pytesseract
    from docx import Document
except ImportError:
    # Graceful handling if deps missing (checked at runtime)
    logger.warning("PdfOCR: Optional OCR dependencies not installed (pdfminer, pdf2image, pytesseract).")

class OCRError(Exception):
    """Custom exception for OCR failures."""
    pass

class PdfOCR:
    """
    Handles OCR for scanned PDFs.
    """
    
    def __init__(self, text_threshold: int = 300):
        """
        Args:
            text_threshold: Character count below which a PDF is considered scanned.
        """
        self.text_threshold = text_threshold

    def is_scanned(self, pdf_path: str) -> bool:
        """
        Check if PDF is scanned (has little/no extractable text).
        """
        try:
            text = extract_text(pdf_path)
            # Simple heuristic: clean whitespace and check length
            clean_text = "".join(text.split())
            return len(clean_text) < self.text_threshold
        except Exception as exc:
            # If pdfminer fails, default to not-scanned so LibreOffice can try.
            logger.warning("PdfOCR.is_scanned: text extraction failed for '%s': %s", pdf_path, exc)
            return False

    def convert_to_docx(self, pdf_path: str, output_path: str) -> str:
        """
        Convert scanned PDF to DOCX via OCR.
        
        Returns:
            Extracted text content (for logging/debugging)
        """
        try:
            # 1. PDF -> Images
            # Poppler check implicitly happens here
            images = convert_from_path(pdf_path)
        except Exception as e:
            raise OCRError(f"Failed to convert PDF to images (Poppler missing?): {e}")

        full_text = []

        # 2. OCR Images — isolate per-page so one bad page doesn't abort all
        for i, image in enumerate(images):
            try:
                page_text = pytesseract.image_to_string(image)
                full_text.append(page_text)
            except Exception as exc:
                logger.warning("PdfOCR: Tesseract failed on page %d: %s", i + 1, exc)
                full_text.append("")  # preserve page slot with empty string

        if not any(full_text):
            raise OCRError("Tesseract OCR produced no text for any page.")

        # 3. Create DOCX
        try:
            doc = Document()
            combined_text = "\n".join(full_text)
            # Basic cleanup: invalid XML chars are handled by python-docx mostly, 
            # but Tesseract output might contain control chars.
            valid_chars_text = "".join(c for c in combined_text if c.isprintable() or c in "\n\r\t")
            doc.add_paragraph(valid_chars_text)
            doc.save(output_path)
            return valid_chars_text
        except Exception as e:
            raise OCRError(f"Failed to save OCR DOCX: {e}")
