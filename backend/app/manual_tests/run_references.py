"""
Manual test script for reference parsing.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models import Document, Block, BlockType
from app.pipeline.references.parser import parse_references

def test_reference_parsing():
    """Test reference parsing on mock blocks."""
    print("\n" + "=" * 70)
    print("REFERENCE PARSING TEST")
    print("=" * 70)
    
    # Create mock document
    doc = Document(document_id="ref_test", original_filename="refs.docx")
    
    # Mock Reference Blocks
    ref_texts = [
        '[1] J. Smith and A. Doe, "Automating Science with AI," IEEE Trans. Auto., vol. 1, 2020.',
        '[2] B. Jones, "Deep Learning for Text," in Proc. CVPR, 2019.',
        '[3] C. Lee. The Future of Work. Springer, 2021.',
        '[Ref4] D. Wang, "Unstructured Data," arXiv:2001.12345, 2020.'
    ]
    
    blocks = []
    for i, text in enumerate(ref_texts):
        blocks.append(Block(
            block_id=f"blk_{i}",
            text=text,
            index=i,
            block_type=BlockType.REFERENCE_ENTRY
        ))
    
    doc.blocks = blocks
    
    # Run Parser
    print(f"Parsing {len(blocks)} references...")
    doc = parse_references(doc)
    
    # Analyze Results
    print("\nParsed References:")
    for ref in doc.references:
        print(f"\nID: {ref.citation_key}")
        print(f"  Type: {ref.reference_type}")
        print(f"  Title: {ref.title}")
        print(f"  Authors: {ref.authors}")
        print(f"  Year: {ref.year}")
        if ref.journal: print(f"  Journal: {ref.journal}")
        if ref.conference: print(f"  Conf: {ref.conference}")
        
    # Validation
    r1 = doc.references[0]
    if r1.year != 2020 or "Smith" not in r1.authors[0]:
        print("❌ Ref 1 mismatch")
    else:
        print("✅ Ref 1 (IEEE) passed")
        
    r2 = doc.references[1]
    if r2.reference_type != "conference_paper" or r2.year != 2019:
        print("❌ Ref 2 mismatch")
    else:
        print("✅ Ref 2 (Conf) passed")

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")

if __name__ == "__main__":
    test_reference_parsing()
