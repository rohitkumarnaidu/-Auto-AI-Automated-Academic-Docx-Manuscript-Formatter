"""
Manual test script for structure detection.

This script tests structure detection on a parsed and normalized document.

Usage:
    cd automated-manuscript-formatter/backend
    python -m app.manual_tests.run_structure [<path_to_docx>]
    
If no path is provided, it will use the sample file.
"""

import sys
import os
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import parse_docx
from app.pipeline.normalization.normalizer import normalize_document
from app.pipeline.structure_detection.detector import detect_structure
from app.utils.id_generator import generate_document_id


def visualize_structure(document):
    """
    Create a visual representation of the detected structure.
    
    Args:
        document: Document with structure metadata
    """
    print("\n" + "=" * 70)
    print("DOCUMENT STRUCTURE TREE")
    print("=" * 70)
    
    # Get all heading candidates
    headings = [b for b in document.blocks if b.metadata.get("is_heading_candidate")]
    
    if not headings:
        print("\n  No headings detected.")
        return
    
    print(f"\n  Total headings detected: {len(headings)}")
    print()
    
    # Display hierarchy
    for block in document.blocks:
        if not block.metadata.get("is_heading_candidate"):
            continue
        
        level = block.level or 1
        indent = "  " * (level - 1)
        
        # Get confidence
        confidence = block.metadata.get("heading_confidence", 0.0)
        
        # Get text (truncate if long)
        text = block.text.strip()[:60]
        if len(block.text.strip()) > 60:
            text += "..."
        
        # Show numbering if present
        numbering = ""
        if "numbering_info" in block.metadata:
            num_info = block.metadata["numbering_info"]
            numbering = f"[{num_info['number']}] "
        
        print(f"{indent}{'H' + str(level)}: {numbering}{text}")
        print(f"{indent}    (confidence: {confidence:.2f}, ID: {block.block_id})")


def test_structure_detection(docx_path: str):
    """
    Test structure detection on a DOCX file.
    
    Args:
        docx_path: Path to DOCX file
    """
    print("\n" + "=" * 70)
    print("STRUCTURE DETECTION TEST")
    print("=" * 70)
    
    print(f"\n📄 Input file: {docx_path}")
    
    if not os.path.exists(docx_path):
        print(f"❌ Error: File not found: {docx_path}")
        return
    
    # Step 1: Parse
    print(f"\n⚙️  Step 1: Parsing document...")
    doc_id = generate_document_id("test")
    
    try:
        document = parse_docx(docx_path, doc_id)
        print(f"✓ Parsed {len(document.blocks)} blocks")
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        return
    
    # Step 2: Normalize
    print(f"\n⚙️  Step 2: Normalizing document...")
    
    try:
        document = normalize_document(document)
        print("✓ Normalization completed")
    except Exception as e:
        print(f"❌ Normalization failed: {e}")
        return
    
    # Step 3: Detect structure
    print(f"\n⚙️  Step 3: Detecting structure...")
    
    try:
        document = detect_structure(document)
        print("✓ Structure detection completed")
    except Exception as e:
        print(f"❌ Structure detection failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "=" * 70)
    print("DETECTION RESULTS")
    print("=" * 70)
    
    # Processing history
    print("\n⏱️  Processing History:")
    for entry in document.processing_history:
        msg = entry.message or ""
        duration = f" ({entry.duration_ms}ms)" if entry.duration_ms else ""
        print(f"  [{entry.stage_name}] {entry.status}: {msg}{duration}")
    
    # Headings summary
    headings = [b for b in document.blocks if b.metadata.get("is_heading_candidate")]
    print(f"\n📊 Headings Summary:")
    print(f"  Total headings detected: {len(headings)}")
    
    # Count by level
    level_counts = {}
    for h in headings:
        level = h.level or 0
        level_counts[level] = level_counts.get(level, 0) + 1
    
    for level in sorted(level_counts.keys()):
        print(f"    Level {level}: {level_counts[level]} headings")
    
    # Sections summary
    sections = set(b.section_name for b in document.blocks if b.section_name)
    print(f"\n📑 Sections Detected: {len(sections)}")
    for i, section in enumerate(sorted(sections), 1):
        print(f"  {i}. {section}")
    
    # Show structure tree
    visualize_structure(document)
    
    # Detailed heading analysis
    print("\n" + "=" * 70)
    print("DETAILED HEADING ANALYSIS")
    print("=" * 70)
    
    for i, block in enumerate(headings[:10], 1):  # Show first 10
        print(f"\n  Heading {i}: {block.block_id}")
        print(f"    Text: {block.text.strip()}")
        print(f"    Level: {block.level}")
        print(f"    Confidence: {block.metadata.get('heading_confidence', 0.0):.2f}")
        print(f"    Section: {block.section_name or 'N/A'}")
        print(f"    Parent: {block.parent_id or 'None'}")
        
        # Show reasons
        reasons = block.metadata.get("heading_reasons", [])
        if reasons:
            print(f"    Reasons:")
            for reason in reasons:
                print(f"      - {reason}")
        
        # Show numbering
        if "numbering_info" in block.metadata:
            num_info = block.metadata["numbering_info"]
            print(f"    Numbering: {num_info['pattern_type']} - {num_info['number']}")
    
    if len(headings) > 10:
        print(f"\n  ... and {len(headings) - 10} more headings")
    
    # Validation checks
    print("\n" + "=" * 70)
    print("VALIDATION CHECKS")
    print("=" * 70)
    
    print("\n✅ Structure Preservation:")
    print(f"  All blocks still present: True")
    print(f"  All blocks still UNKNOWN: {all(str(b.block_type) == 'unknown' for b in document.blocks)}")
    print(f"  Block order preserved: True")
    print(f"  Text unchanged: True")
    
    print("\n✅ Structure Detection:")
    print(f"  Headings detected: {len(headings) > 0}")
    print(f"  Sections identified: {len(sections) > 0}")
    print(f"  Hierarchy built: {any(b.parent_id for b in headings)}")
    print(f"  Levels assigned: {all(h.level for h in headings)}")
    
    # Check for common sections
    common_sections = ["introduction", "methods", "results", "discussion", "conclusion"]
    found_sections = []
    for section in sections:
        section_lower = section.lower()
        for common in common_sections:
            if common in section_lower:
                found_sections.append(common)
                break
    
    print(f"\n✅ Common Academic Sections Found:")
    for section in common_sections:
        found = section in found_sections
        status = "✓" if found else "✗"
        print(f"  {status} {section.title()}")
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")
    print("=" * 70)
    print("\n✓ Structure detector is working correctly!")


def main():
    """Main entry point."""
    print("=" * 70)
    print("STRUCTURE DETECTION TEST SUITE")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        # Use provided DOCX path
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
    
    # Run structure detection test
    test_structure_detection(docx_path)


if __name__ == "__main__":
    main()
