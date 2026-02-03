"""
Manual test script for document validation.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models import Document, Block, BlockType, Figure, Reference, ReferenceType
from app.pipeline.validation.validator import validate_document

def test_validation():
    """Test validation logic on mock document."""
    print("\n" + "=" * 70)
    print("VALIDATION TEST")
    print("=" * 70)
    
    # 1. Create a Good Document
    doc_good = Document(document_id="good_doc", original_filename="good.docx")
    
    # Sections (Abstract, Intro, Refs)
    doc_good.blocks = [
        Block(block_id="b1", text="Abstract", block_type=BlockType.ABSTRACT_HEADING, index=0, section_name="Abstract"),
        Block(block_id="b2", text="Introduction", block_type=BlockType.HEADING_1, index=1, section_name="Introduction"),
        Block(block_id="b3", text="References", block_type=BlockType.REFERENCES_HEADING, index=2, section_name="References"),
    ]
    # Figures with captions
    fig = Figure(figure_id="f1", index=0, caption_text="Fig 1. Test")
    doc_good.figures = [fig]
    # References complete
    ref = Reference(reference_id="r1", citation_key="[1]", raw_text="...", index=0,
                   # Missing nothing critical for now. Wait, created without fields.
                   year=2020, authors=["Smith"], title="Paper")
    doc_good.references = [ref]
    
    print("\n[Case 1] Valid Document:")
    res = validate_document(doc_good)
    print(f"  Valid: {res.is_valid}")
    print(f"  Errors: {res.errors}")
    print(f"  Warnings: {res.warnings}")
    
    if res.is_valid and not res.errors:
        print("  ✅ Passed (Clean)")
    else:
        print("  ❌ Failed (Unexpected errors)")

    # 2. Create a Bad Document
    doc_bad = Document(document_id="bad_doc", original_filename="bad.docx")
    # No sections, Uncaptioned figure, Bad reference
    doc_bad.blocks = []
    
    doc_bad.figures = [
        Figure(figure_id="f2", index=0, caption_text="") # Missing caption
    ]
    doc_bad.references = [
         Reference(reference_id="r2", citation_key="[2]", raw_text="...", index=0,
                   year=None, authors=[], title=None) # Bad ref
    ]
    
    print("\n[Case 2] Invalid Document:")
    res = validate_document(doc_bad)
    print(f"  Valid: {res.is_valid}")
    print(f"  Errors: {res.errors}")
    print(f"  Warnings: {res.warnings}")
    
    print(f"  Valid: {res.is_valid}")
    print(f"  Errors: {res.errors}")
    print(f"  Warnings: {res.warnings}")
    
    expected_errors = ["Missing References section"]
    expected_warnings = [
        "Missing Abstract section",
        "Missing Introduction section",
        "Figure f2 missing caption",
        "Reference '[2]' missing publication year",
    ]
    
    found_errors = all(any(e in err for err in res.errors) for e in expected_errors)
    found_warnings = any("Abstract" in w for w in res.warnings) and \
                     any("figure" in w.lower() for w in res.warnings)
                     
    if not res.is_valid and found_errors and found_warnings:
        print("  ✅ Passed (Correct detection)")
    else:
        print("  ❌ Failed (Did not detect expected issues)")
        
    # 3. Figure Reference Logic
    print("\n[Case 3] Figure Reference Mismatch:")
    doc_ref = Document(document_id="ref_check", original_filename="test.docx")
    
    # Text references Figure 2, but we only have 1 figure
    doc_ref.blocks = [
        Block(block_id="b1", text="See Figure 2 for details.", block_type=BlockType.BODY, index=0, section_name="Body"),
        Block(block_id="b2", text="References", block_type=BlockType.REFERENCES_HEADING, index=1, section_name="References")
    ]
    doc_ref.figures = [Figure(figure_id="f1", index=0, caption_text="Fig 1")] # Count: 1
    
    res_ref = validate_document(doc_ref)
    
    found_ref_warning = any("Figure 2 referenced but missing" in w for w in res_ref.warnings)
    if found_ref_warning:
         print(f"  ✅ Passed (Detected missing Figure 2)")
    else:
         print(f"  ❌ Failed (Warnings: {res_ref.warnings})")

    found_ref_warning = any("Figure 2 referenced but missing" in w for w in res_ref.warnings)
    if found_ref_warning:
         print(f"  ✅ Passed (Detected missing Figure 2)")
    else:
         print(f"  ❌ Failed (Warnings: {res_ref.warnings})")

    # 4. Advanced Checks (Tables, Citations)
    print("\n[Case 4] Advanced Checks:")
    doc_adv = Document(document_id="adv_check", original_filename="adv.docx")
    doc_adv.blocks = [
        Block(block_id="b1", text="As shown in [99] and [1]", block_type=BlockType.BODY, index=0),
        Block(block_id="b2", text="References", block_type=BlockType.REFERENCES_HEADING, index=1),
    ]
    # One valid ref [1], one missing [99]
    doc_adv.references = [
        Reference(reference_id="r1", citation_key="[1]", raw_text="...", index=0, year="2000", authors=["A"], title="T")
    ]
    # Uncaptioned table
    # We need to import Table? It might be available via Document models
    from app.models import Table
    doc_adv.tables = [
        Table(table_id="t1", index=0, rows=[["A"]], caption_text="", num_rows=1, num_cols=1) 
    ]
    
    res_adv = validate_document(doc_adv)
    
    found_cit_warn = any("Citation [99] matches no entry" in w for w in res_adv.warnings)
    found_tbl_warn = any("Table 1 missing caption" in w for w in res_adv.warnings)
    
    if found_cit_warn and found_tbl_warn:
        print("  ✅ Passed (Detected citation mismatch and uncaptioned table)")
    else:
        print(f"  ❌ Failed. Warnings: {res_adv.warnings}")

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")

if __name__ == "__main__":
    test_validation()
