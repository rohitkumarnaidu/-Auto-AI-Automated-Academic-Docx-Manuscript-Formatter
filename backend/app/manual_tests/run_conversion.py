"""
Manual test for Input Conversion.
"""

import sys
import os
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.pipeline.input_conversion.converter import InputConverter, ConversionError

def test_conversion():
    print("\n" + "=" * 70)
    print("INPUT CONVERSION TEST")
    print("=" * 70)
    
    converter = InputConverter()
    
    # 1. Test DOCX Pass-through (Mock file)
    print("\n[Case 1] DOCX Pass-through:")
    mock_docx = "test_input.docx"
    with open(mock_docx, "w") as f: f.write("dummy docx content")
    
    try:
        out_path = converter.convert_to_docx(mock_docx, "test_job_1")
        print(f"✅ Converted: {out_path}")
        if os.path.exists(out_path):
            print("   File exists.")
    except Exception as e:
        print(f"❌ Failed: {e}")
    finally:
        if os.path.exists(mock_docx): os.remove(mock_docx)

    # 2. Test Markdown (Requires Pandoc)
    print("\n[Case 2] Markdown -> DOCX (Pandoc):")
    if shutil.which("pandoc"):
        mock_md = "test_input.md"
        with open(mock_md, "w") as f: f.write("# Title\n\nBody text.")
        
        try:
            out_path = converter.convert_to_docx(mock_md, "test_job_2")
            print(f"✅ Converted: {out_path}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        finally:
            if os.path.exists(mock_md): os.remove(mock_md)
    else:
        print("⚠️ Skipped (Pandoc not installed)")

    # 3. Test Unsupported Format
    print("\n[Case 3] Unsupported Format (.xyz):")
    mock_xyz = "test.xyz"
    with open(mock_xyz, "w") as f: f.write("data")
    
    try:
        converter.convert_to_docx(mock_xyz, "test_job_3")
        print("❌ Failed (Should have raised error)")
    except ConversionError as e:
        print(f"✅ Correctly caught error: {e}")
    finally:
        if os.path.exists(mock_xyz): os.remove(mock_xyz)

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")

if __name__ == "__main__":
    test_conversion()
