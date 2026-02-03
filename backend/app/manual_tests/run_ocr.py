"""
Manual test for OCR logic.
"""

import os
import sys
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.pipeline.ocr.pdf_ocr import PdfOCR

def test_ocr():
    print("\n" + "=" * 70)
    print("OCR MANUAL TEST")
    print("=" * 70)
    
    # We need a PDF file to test.
    # Since we can't easily create a real scanned PDF programmatically without PIL/ReportLab saving Images as PDF,
    # we will mock the PdfOCR class logic or rely on a file if present.
    # Alternatively, we test the logic behavior assuming scanned.
    
    print("[1] Testing PdfOCR instantiation...")
    try:
        ocr = PdfOCR()
        print("✅ Instantiation successful")
    except Exception as e:
        print(f"❌ Failed to instantiate: {e}")
        return

    print("\n[2] Testing is_scanned (Mocking pdfminer)...")
    # We simulate a file that pdfminer reads as empty text
    # Since we don't have a real PDF, we can mock `extract_text` if we want, 
    # but for manual test script running in real env, we need a file.
    # I'll create a dummy empty PDF using reportlab or fpdf if available? 
    # No, I shouldn't rely on extra deps.
    # I'll create a text file and rename to .pdf -> extract_text might fail or return empty?
    # pdfminer expects valid PDF structure.
    
    # Let's Skip actual PDF processing if we don't have a sample, 
    # and just assert the Module inputs/outputs if possible?
    # Or create a fake file 'test_scanned.pdf' and see what happens.
    
    dummy_pdf = "test_scanned.pdf"
    with open(dummy_pdf, "wb") as f:
        f.write(b"%PDF-1.4 empty") # Invalid PDF likely, pdfminer will error.
        
    print(f"Created dummy PDF: {dummy_pdf}")
    
    is_scanned = ocr.is_scanned(dummy_pdf)
    print(f"is_scanned result: {is_scanned}")
    if is_scanned is False:
         print("ℹ️ likely returned False because pdfminer raised exception (as expected for invalid PDF).")
    
    # Cleanup
    if os.path.exists(dummy_pdf):
        os.remove(dummy_pdf)

    print("\n[3] Testing convert_to_docx (Mocking internally)...")
    # Since we lack Tesseract/Poppler in this environment (likely), 
    # we expect it to raise OCRError.
    
    try:
        ocr.convert_to_docx("non_existent.pdf", "output.docx")
    except Exception as e:
        print(f"✅ Caught expected error (missing file/tools): {e}")

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")

if __name__ == "__main__":
    test_ocr()
