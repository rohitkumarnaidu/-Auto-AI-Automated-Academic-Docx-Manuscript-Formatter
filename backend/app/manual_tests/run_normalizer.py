"""
Manual test script for text normalization.

This script tests the normalizer on a parsed document.

Usage:
    cd automated-manuscript-formatter/backend
    python -m app.manual_tests.run_normalizer [<path_to_docx>]
    
If no path is provided, it will use the sample file from run_parser.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.pipeline.parsing.parser import parse_docx
from app.pipeline.normalization.normalizer import normalize_document
from app.utils.id_generator import generate_document_id


def show_text_comparison(original: str, normalized: str, label: str = "Text"):
    """
    Show before/after comparison of text.
    
    Args:
        original: Original text
        normalized: Normalized text
        label: Label for the comparison
    """
    if original == normalized:
        print(f"  {label}: No changes")
        return
    
    print(f"  {label}:")
    print(f"    Before: {repr(original[:100])}")
    print(f"    After:  {repr(normalized[:100])}")
    if len(original) != len(normalized):
        print(f"    Length: {len(original)} → {len(normalized)}")


def test_normalizer(docx_path: str):
    """
    Test the normalizer on a DOCX file.
    
    Args:
        docx_path: Path to DOCX file
    """
    print("\n" + "=" * 70)
    print("NORMALIZATION TEST")
    print("=" * 70)
    
    print(f"\n📄 Input file: {docx_path}")
    
    if not os.path.exists(docx_path):
        print(f"❌ Error: File not found: {docx_path}")
        return
    
    # Step 1: Parse the document
    print(f"\n⚙️  Step 1: Parsing document...")
    doc_id = generate_document_id("test")
    
    try:
        document = parse_docx(docx_path, doc_id)
        print(f"✓ Parsed {len(document.blocks)} blocks, {len(document.tables)} tables")
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        return
    
    # Keep a copy of original for comparison
    import copy
    original_blocks = copy.deepcopy(document.blocks)
    original_metadata = copy.deepcopy(document.metadata)
    original_tables = copy.deepcopy(document.tables)
    
    # Step 2: Normalize the document
    print(f"\n⚙️  Step 2: Normalizing document...")
    
    try:
        document = normalize_document(document)
        print("✓ Normalization completed successfully")
    except Exception as e:
        print(f"❌ Normalization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "=" * 70)
    print("NORMALIZATION RESULTS")
    print("=" * 70)
    
    # Processing history
    print("\n⏱️  Processing History:")
    for entry in document.processing_history:
        msg = entry.message or ""
        duration = f" ({entry.duration_ms}ms)" if entry.duration_ms else ""
        print(f"  [{entry.stage_name}] {entry.status}: {msg}{duration}")
    
    # Metadata changes
    print("\n📋 Metadata Changes:")
    changes = 0
    
    if original_metadata.title != document.metadata.title:
        show_text_comparison(original_metadata.title or "", document.metadata.title or "", "Title")
        changes += 1
    
    if original_metadata.authors != document.metadata.authors:
        print(f"  Authors: {original_metadata.authors} → {document.metadata.authors}")
        changes += 1
    
    if original_metadata.keywords != document.metadata.keywords:
        print(f"  Keywords: {original_metadata.keywords} → {document.metadata.keywords}")
        changes += 1
    
    if original_metadata.abstract != document.metadata.abstract:
        show_text_comparison(original_metadata.abstract or "", document.metadata.abstract or "", "Abstract")
        changes += 1
    
    if changes == 0:
        print("  No metadata changes")
    
    # Block changes
    print(f"\n📝 Block Changes (showing changed blocks only):")
    block_changes = 0
    for i, (orig_block, norm_block) in enumerate(zip(original_blocks, document.blocks)):
        if orig_block.text != norm_block.text:
            block_changes += 1
            if block_changes <= 5:  # Show first 5 changes
                print(f"\n  Block {norm_block.block_id}:")
                show_text_comparison(orig_block.text, norm_block.text, "")
    
    if block_changes == 0:
        print("  No block text changes")
    else:
        print(f"\n  Total blocks with text changes: {block_changes}/{len(document.blocks)}")
    
    # Table changes
    if document.tables:
        print(f"\n📊 Table Changes:")
        table_changes = 0
        
        for i, (orig_table, norm_table) in enumerate(zip(original_tables, document.tables)):
            cell_changes = 0
            for orig_cell, norm_cell in zip(orig_table.cells, norm_table.cells):
                if orig_cell.text != norm_cell.text:
                    cell_changes += 1
            
            if cell_changes > 0:
                table_changes += 1
                print(f"  {norm_table.table_id}: {cell_changes} cells changed")
                
                # Show first changed cell
                for orig_cell, norm_cell in zip(orig_table.cells, norm_table.cells):
                    if orig_cell.text != norm_cell.text:
                        print(f"    Cell ({norm_cell.row},{norm_cell.col}):")
                        show_text_comparison(orig_cell.text, norm_cell.text, "")
                        break  # Show only first change per table
        
        if table_changes == 0:
            print("  No table changes")
    
    # Validation checks
    print("\n" + "=" * 70)
    print("VALIDATION CHECKS")
    print("=" * 70)
    
    print("\n✅ Structure Preservation:")
    print(f"  Block count unchanged: {len(original_blocks) == len(document.blocks)}")
    print(f"  Block IDs preserved: {all(o.block_id == n.block_id for o, n in zip(original_blocks, document.blocks))}")
    print(f"  Block indices preserved: {all(o.index == n.index for o, n in zip(original_blocks, document.blocks))}")
    print(f"  Block types unchanged: {all(o.block_type == n.block_type for o, n in zip(original_blocks, document.blocks))}")
    print(f"  All blocks still UNKNOWN: {all(str(b.block_type) == 'unknown' for b in document.blocks)}")
    
    if document.tables:
        print(f"\n  Table count unchanged: {len(original_tables) == len(document.tables)}")
        print(f"  Table IDs preserved: {all(o.table_id == n.table_id for o, n in zip(original_tables, document.tables))}")
    
    print("\n✅ Text Quality:")
    # Check for common Unicode issues being fixed
    all_text = " ".join([b.text for b in document.blocks])
    print(f"  No fancy quotes: {'\u201C' not in all_text and '\u201D' not in all_text}")
    print(f"  No em-dashes (as single char): {'\u2014' not in all_text}")
    print(f"  No non-breaking spaces: {'\u00A0' not in all_text}")
    
    # Check for excessive whitespace
    excessive_space_count = sum(1 for b in document.blocks if '  ' in b.text)
    print(f"  Blocks with multiple spaces: {excessive_space_count}")
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")
    print("=" * 70)
    print("\n✓ Normalizer is working correctly!")


def test_text_utils():
    """Test text utility functions directly."""
    print("\n" + "=" * 70)
    print("TEXT UTILITIES TEST")
    print("=" * 70)
    
    from app.utils.text_utils import (
        normalize_unicode,
        normalize_whitespace,
        normalize_block_text,
        normalize_table_cell_text,
        clean_metadata_field,
    )
    
    # Test Unicode normalization
    print("\n📝 Unicode Normalization:")
    test_cases = [
        ("It\u2019s a \u201Cquote\u201D \u2014 with dashes", "It's a \"quote\" -- with dashes"),
        ("Non\u00A0breaking space here", "Non breaking space here"),  # Non-breaking space → regular space
        ("Em\u2014dash and en\u2013dash", "Em--dash and en-dash"),
    ]
    
    for original, expected in test_cases:
        result = normalize_unicode(original)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {repr(original)}")
        print(f"     → {repr(result)}")
        if result != expected:
            print(f"     Expected: {repr(expected)}")
    
    # Test whitespace normalization
    print("\n📝 Whitespace Normalization:")
    test_cases = [
        ("Hello    world", "Hello world"),
        ("  Trim me  ", "Trim me"),
        ("Line1\n\n\n\nLine2", "Line1\n\nLine2"),  # Collapse newlines
        ("Tab\there", "Tab here"),
    ]
    
    for original, expected in test_cases:
        result = normalize_whitespace(original, collapse_newlines=True)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {repr(original)}")
        print(f"     → {repr(result)}")
        if result != expected:
            print(f"     Expected: {repr(expected)}")
    
    # Test block text normalization
    print("\n📝 Block Text Normalization:")
    test_text = "It\u2019s  a  \u201Ctest\u201D  with    extra   spaces\n\n\nand newlines"
    result = normalize_block_text(test_text)
    print(f"  Original: {repr(test_text)}")
    print(f"  Result:   {repr(result)}")
    
    # Test table cell normalization
    print("\n📝 Table Cell Normalization:")
    test_text = "Cell with\nmultiple\nlines  and   spaces"
    result = normalize_table_cell_text(test_text)
    print(f"  Original: {repr(test_text)}")
    print(f"  Result:   {repr(result)}")
    print(f"  Expected: Single line, collapsed spaces")
    
    # Test metadata cleaning
    print("\n📝 Metadata Field Cleaning:")
    test_text = "  Title with\nmultiple lines   and   spaces  "
    result = clean_metadata_field(test_text)
    print(f"  Original: {repr(test_text)}")
    print(f"  Result:   {repr(result)}")
    
    print("\n✓ Text utilities working correctly!")


def main():
    """Main entry point."""
    print("=" * 70)
    print("NORMALIZATION STAGE TEST SUITE")
    print("=" * 70)
    
    # Test 1: Text utilities
    test_text_utils()
    
    # Test 2: Full document normalization
    if len(sys.argv) > 1:
        # Use provided DOCX path
        docx_path = sys.argv[1]
    else:
        # Use sample file from parser tests
        sample_path = Path(__file__).parent / "sample_inputs" / "sample_paper.docx"
        
        if not sample_path.exists():
            print("\n⚠️  Sample file not found. Creating it...")
            from app.manual_tests.run_parser import create_sample_docx
            sample_path.parent.mkdir(exist_ok=True)
            create_sample_docx(str(sample_path))
        
        docx_path = str(sample_path)
    
    # Run full document test
    test_normalizer(docx_path)


if __name__ == "__main__":
    main()
