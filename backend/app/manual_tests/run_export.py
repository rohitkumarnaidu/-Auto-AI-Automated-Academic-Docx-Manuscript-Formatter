"""
Manual test for Formatting and Export.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models import Document, Block, BlockType, Figure
from app.pipeline.formatting.formatter import Formatter
from app.pipeline.export.exporter import Exporter

def test_pipeline_export():
    print("\n" + "=" * 70)
    print("FORMATTING & EXPORT TEST")
    print("=" * 70)
    
    # 1. Mock Document
    doc = Document(document_id="export_test", original_filename="test.docx")
    doc.blocks = [
        Block(block_id="b1", text="My Title", block_type=BlockType.TITLE, index=0),
        Block(block_id="b2", text="Introduction", block_type=BlockType.HEADING_1, index=1),
        Block(block_id="b3", text="This is the body text.", block_type=BlockType.BODY, index=2),
    ]
    # Add a dummy figure
    # (Without binary data for this test, placeholder logic should trigger)
    fig = Figure(figure_id="f1", index=0, caption_text="Test Figure", metadata={"block_index": 2})
    doc.figures = [fig]
    
    outputPath = os.path.abspath("test_output/formatted_doc.docx")
    
    # 2. Test WITHOUT Template (Should Skip)
    print("\n[Case 1] No Template:")
    formatter = Formatter()
    wdoc = formatter.format(doc, template_name=None)
    
    if wdoc is None:
        print("✅ Correctly skipped formatting (None returned)")
    else:
        print("❌ Error: Returned document when none expected")
        
    # 3. Test WITH Template (Should Work)
    # We need a dummy template/contract or rely on defaults.
    # The formatter logic handles missing files by using default Doc().
    print("\n[Case 2] Dummy Template Name:")
    wdoc2 = formatter.format(doc, template_name="test_template_dummy")
    
    if wdoc2:
        print("✅ Generated docx object")
        
        # Test Export
        exporter = Exporter()
        saved_path = exporter.export(wdoc2, outputPath)
        
        if os.path.exists(saved_path):
            print(f"✅ Saved file at: {saved_path}")
        else:
            print("❌ File write failed")
    else:
        print("❌ Failed to generate document")

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")

if __name__ == "__main__":
    test_pipeline_export()
