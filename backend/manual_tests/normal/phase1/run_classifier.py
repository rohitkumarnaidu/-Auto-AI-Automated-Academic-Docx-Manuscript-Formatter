"""
Manual test script for content classification.

Tests the assignment of semantic BlockTypes to blocks.
"""

import sys
import os
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import parse_docx
from app.pipeline.normalization.normalizer import normalize_document
from app.pipeline.structure_detection.detector import detect_structure
from app.pipeline.classification.classifier import classify_content
from app.utils.id_generator import generate_document_id
from app.models.block import BlockType


def test_classification(docx_path: str):
    """
    Test classification on a DOCX file.
    """
    print("\n" + "=" * 70)
    print("CLASSIFICATION TEST")
    print("=" * 70)
    
    print(f"\n📄 Input file: {docx_path}")
    
    if not os.path.exists(docx_path):
        print(f"❌ Error: File not found: {docx_path}")
        return
    
    # Run Pipeline Stages
    print(f"\n⚙️  Running pipeline stages...")
    
    try:
        doc_id = generate_document_id("test")
        
        # 1. Parse
        document = parse_docx(docx_path, doc_id)
        print(f"  ✓ Parsed ({len(document.blocks)} blocks)")
        
        # 2. Normalize
        document = normalize_document(document)
        print(f"  ✓ Normalized")
        
        # 3. Structure
        document = detect_structure(document)
        print(f"  ✓ Structure Detected")
        
        # 4. Classify (Target)
        print(f"  > Classifying content...")
        document = classify_content(document)
        print(f"  ✓ Classification Complete")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Analyze Results
    print("\n" + "=" * 70)
    print("CLASSIFICATION RESULTS")
    print("=" * 70)
    
    # 1. Type Distribution
    print(f"\n📊 Type Distribution:")
    type_counts = {}
    for block in document.blocks:
        btype = block.block_type
        type_counts[btype] = type_counts.get(btype, 0) + 1
        
    for btype in sorted(type_counts.keys()):
        print(f"  {btype}: {type_counts[btype]}")

    # 2. Sequential Block Walkthrough (Condensed)
    print(f"\n📝 Document Flow:")
    
    current_section = None
    
    # Helper to format block preview
    def fmt_block(b):
        text = b.text.strip().replace('\n', ' ')
        if len(text) > 50: text = text[:47] + "..."
        type_tag = b.block_type.value.upper()
        return f"[{type_tag}] {text}"

    for i, block in enumerate(document.blocks):
        if not block.text.strip():
            continue # Skip empty for clean output
            
        print(f"  {i:03d} {fmt_block(block)}")

    # 3. Validation Logic
    print("\n" + "=" * 70)
    print("VALIDATION CHECKS")
    print("=" * 70)
    
    unknown_blocks = [b for b in document.blocks if b.block_type == BlockType.UNKNOWN]
    print(f"\n✅ Unknown Blocks Eliminated: {'PASS' if not unknown_blocks else 'FAIL'}")
    if unknown_blocks:
        print(f"  Found {len(unknown_blocks)} UNKNOWN blocks.")

    # Check for specific expected content
    titles = [b for b in document.blocks if b.block_type == BlockType.TITLE]
    authors = [b for b in document.blocks if b.block_type == BlockType.AUTHOR]
    abstract_heads = [b for b in document.blocks if b.block_type == BlockType.ABSTRACT_HEADING]
    
    print(f"  Title Found: {len(titles) > 0}")
    print(f"  Authors Found: {len(authors) > 0}")
    print(f"  Abstract Found: {len(abstract_heads) > 0}")
    
    # Check References
    ref_entries = [b for b in document.blocks if b.block_type == BlockType.REFERENCE_ENTRY]
    print(f"  References Found: {len(ref_entries) > 0}")
    if ref_entries:
        print(f"    (Found {len(ref_entries)} entries)")

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")
    print("=" * 70)


def main():
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        # Use sample file
        sample_path = Path(__file__).parent / "sample_inputs" / "sample_paper.docx"
        
        if not sample_path.exists():
            print("\n⚠️  Sample file not found. Creating it...")
            from app.manual_tests.run_parser import create_sample_docx
            sample_path.parent.mkdir(exist_ok=True)
            create_sample_docx(str(sample_path))
        
        docx_path = str(sample_path)
    
    test_classification(docx_path)


if __name__ == "__main__":
    main()
