"""
Phase 3 - Step 10: Formatter Test

Purpose: Apply formatting to validated PipelineDocument
Tests: Formatter ONLY (assumes identification is correct)

Usage:
    python manual_tests/phase3_formatting/run_formatter.py sample_inputs/simple.docx --template IEEE

Output:
    manual_tests/outputs/10_formatted.docx

Success Criteria:
    - DOCX generated successfully
    - Open in Word for manual inspection
    - No duplication
    - Correct heading styles
    - Proper caption placement
"""

import sys
import os
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# Fallback if running from backend root
if os.path.abspath(".").endswith("backend") and os.path.abspath(".") not in sys.path:
    sys.path.insert(0, os.path.abspath("."))

from app.models import PipelineDocument, DocumentMetadata
from app.pipeline.parsing.parser import DocxParser
from app.pipeline.intelligence.semantic_parser import SemanticParser
from app.pipeline.formatting.formatter import Formatter

def main():
    parser = argparse.ArgumentParser(description='Phase 3: Formatter Test')
    parser.add_argument('input', help='Input DOCX file')
    parser.add_argument('--template', default='IEEE', choices=['IEEE', 'Springer', 'APA', 'none'],
                       help='Template to use (default: IEEE)')
    
    args = parser.parse_args()
    
    input_path = args.input
    template = args.template
    output_dir = Path(__file__).parent.parent / "outputs"
    output_path = output_dir / f"10_formatted_{template.lower()}.docx"
    
    print("=" * 60)
    print("PHASE 3 - STEP 10: FORMATTER TEST")
    print("=" * 60)
    print(f"Input: {input_path}")
    print(f"Template: {template}")
    print(f"Output: {output_path}")
    print()
    
    try:
        # Run identification pipeline (Phase 1 + 2)
        print("[1/2] Running identification pipeline...")
        docx_parser = DocxParser()
        # Original: doc_obj = docx_parser.parse(input_path, document_id="test_manual")
        # Manually create PipelineDocument for testing formatter with predefined metadata
        doc_obj = PipelineDocument(
            document_id="export_test", 
            original_filename="test.docx",
            metadata=DocumentMetadata(
                title="Test Paper",
                authors=["Test Author"],
                affiliations=[],
                abstract="",
                keywords=[],
                ai_hints={}
            )
        )
        # Parse blocks from the input DOCX, but assign them to the manually created doc_obj
        # This allows testing formatter with real content but controlled metadata
        parsed_doc_with_blocks = docx_parser.parse(input_path, document_id="test_manual")
        doc_obj.blocks = parsed_doc_with_blocks.blocks
        
        semantic_parser = SemanticParser()
        doc_obj.blocks = semantic_parser.detect_boundaries(doc_obj.blocks)
        
        print(f"      Identified {len(doc_obj.blocks)} blocks")
        
        # Apply formatting
        print("[2/2] Applying formatting...")
        formatter = Formatter(template=template)
        formatted_path = formatter.format(doc_obj, str(output_path))
        
        print(f"      Formatted DOCX created")
        
    except Exception as e:
        print(f"\n❌ FORMATTING FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"✅ Formatting completed successfully")
    print(f"   Output: {output_path}")
    print()
    print("CRITICAL: MANUAL INSPECTION REQUIRED")
    print("=" * 60)
    print("1. Open the DOCX in Microsoft Word")
    print("2. Check for content duplication:")
    print("   - Are headings duplicated?")
    print("   - Are figures/tables appearing twice?")
    print("   - Are references duplicated?")
    print("3. Verify heading hierarchy:")
    print("   - H1 > H2 > H3 visual distinction")
    print("   - Consistent spacing")
    print("4. Check caption placement:")
    print("   - Figures: caption below")
    print("   - Tables: caption above")
    print("5. Verify reference formatting:")
    print("   - Consistent style")
    print("   - No duplicates")
    print()
    print("⚠️  If issues found:")
    print("    - Document specific problems")
    print("    - Report back before making fixes")
    print("    - Fixes should ONLY touch formatter logic")
    print()

if __name__ == "__main__":
    main()
