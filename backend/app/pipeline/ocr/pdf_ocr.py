"""
PDF OCR Module - Handles scanned PDFs by converting to images and extracting text.
"""

import os
from typing import List, Tuple
try:
    from pdfminer.high_level import extract_text
    from pdf2image import convert_from_path
    import pytesseract
    from docx import Document
except ImportError:
    # Graceful handling if deps missing (checked at runtime)
    pass

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
        except Exception as e:
            # If pdfminer fails, assume it might be corrupt or encrypted, 
            # OR just default to not-scanned (let LibreOffice try)
            # OR default to scanned?
            # User says: "If extracted text length < threshold... Treat as scanned"
            # If we can't extract, maybe it's image only?
            # Let's log and assume scanned if we can't read text? 
            # Or safer: let LibreOffice handle it.
            print(f"Warning: PDF text check failed: {e}")
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
        
        try:
            # 2. OCR Images
            for i, image in enumerate(images):
                # Tesseract check implicitly happens here
                page_text = pytesseract.image_to_string(image)
                full_text.append(page_text)
                
        except Exception as e:
            raise OCRError(f"Tesseract OCR failed: {e}")

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
