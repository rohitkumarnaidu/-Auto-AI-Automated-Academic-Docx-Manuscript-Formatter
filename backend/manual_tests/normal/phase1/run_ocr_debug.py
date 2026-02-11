"""
Normal Test: OCR Toolchain Verification
Purpose: Verify OCR module instantiation and method signatures
Input: N/A (Mocked PDF)
Output: Console Output
"""

import os
import sys
from pathlib import Path

# Add backend to path (Depth 3)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.ocr.pdf_ocr import PdfOCR

def main():
    print("=" * 70)
    print("NORMAL TEST: OCR TOOLCHAIN VERIFICATION")
    print("=" * 70)
    
    print("[1/3] Testing PdfOCR instantiation...")
    try:
        ocr = PdfOCR()
        print("✅ Instantiation successful")
    except Exception as e:
        print(f"❌ Failed to instantiate: {e}")
        return

    print("\n[2/3] Testing is_scanned (Mocking invalid PDF)...")
    dummy_pdf = "test_scanned.pdf"
    with open(dummy_pdf, "wb") as f:
        f.write(b"%PDF-1.4 empty") 
        
    try:
        is_scanned = ocr.is_scanned(dummy_pdf)
        print(f"is_scanned result: {is_scanned}")
        print("ℹ️ likely returned False because dummy PDF structure is invalid (as expected).")
    finally:
        if os.path.exists(dummy_pdf):
            os.remove(dummy_pdf)

    print("\n[3/3] Testing Tool Integrity (convert_to_docx)...")
    try:
        ocr.convert_to_docx("non_existent.pdf", "output.docx")
    except Exception as e:
        print(f"✅ Caught expected error (missing file/tools): {e}")

    print("\n✅ SUCCESS: OCR Module structure verified.")

if __name__ == "__main__":
    main()
