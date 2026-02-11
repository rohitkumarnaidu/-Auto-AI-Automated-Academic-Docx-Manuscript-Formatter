import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.models import Document, Block, BlockType
from app.pipeline.parsing.parser import DocxParser
from app.pipeline.references.parser import parse_references

def test_mock_references():
    """Mock reference parsing test from legacy app/manual_tests/run_references.py"""
    print("\n[Case 1] Running Mock Reference Parsing...")
    doc = Document(document_id="ref_test", original_filename="refs.docx")
    
    ref_texts = [
        '[1] J. Smith and A. Doe, "Automating Science with AI," IEEE Trans. Auto., vol. 1, 2020.',
        '[2] B. Jones, "Deep Learning for Text," in Proc. CVPR, 2019.',
        '[3] C. Lee. The Future of Work. Springer, 2021.',
        '[Ref4] D. Wang, "Unstructured Data," arXiv:2001.12345, 2020.'
    ]
    
    blocks = []
    for i, text in enumerate(ref_texts):
        blocks.append(Block(
            block_id=f"mock_blk_{i}",
            text=text,
            index=i,
            block_type=BlockType.REFERENCE_ENTRY
        ))
    
    doc.blocks = blocks
    doc = parse_references(doc)
    
    print(f"✅ Parsed {len(doc.references)} references.")
    for ref in doc.references:
        print(f"  - [{ref.citation_key}] {ref.title} ({ref.year})")

def main(input_path=None):
    print(f"\n🚀 PHASE 1: REFERENCE DETECTION")
    
    # 1. Run Mock Test
    test_mock_references()

    # 2. Run on actual file if provided
    blocks = []
    if input_path:
        print(f"\n[Case 2] Running on target: {input_path}")
        if not os.path.exists(input_path):
            print(f"❌ ERROR: File not found: {input_path}")
        else:
            parser = DocxParser()
            doc = parser.parse(input_path, "active_test")
            blocks = doc.blocks
            doc = Document(document_id="active_test", original_filename=input_path, blocks=blocks)
            doc = parse_references(doc)
            print(f"✅ Parsed {len(doc.references)} references from file.")

    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "12_references.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_reference_blocks": len([b for b in blocks if b.type == BlockType.REFERENCE_ENTRY]),
                "extracted_references": len(blocks) # Simplified dump
            },
            "blocks": [b.model_dump() for b in blocks if b.type == BlockType.REFERENCE_ENTRY]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Ref Blocks Detected: {len([b for b in blocks if b.type == BlockType.REFERENCE_ENTRY])}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    main(target)
