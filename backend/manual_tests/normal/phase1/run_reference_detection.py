"""
Normal Test: Reference Detection
Purpose: Verify reference parsing logic and save to JSON
Input: DOCX file
Output: manual_tests/outputs/12_references.json
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.models.block import Block, BlockType
from app.pipeline.parsing.parser import DocxParser
from app.pipeline.references.parser import ReferenceParser

def test_mock_references():
    """Mock reference parsing test from legacy app/manual_tests/run_references.py"""
    print("\n[Case 1] Running Mock Reference Parsing...")
    ref_texts = [
        '[1] J. Smith and A. Doe, "Automating Science with AI," IEEE Trans. Auto., vol. 1, 2020.',
        '[2] B. Jones, "Deep Learning for Text," in Proc. CVPR, 2019.',
        '[3] C. Lee. The Future of Work. Springer, 2021.',
        '[Ref4] D. Wang, "Unstructured Data," arXiv:2001.12345, 2020.'
    ]
    
    parser = ReferenceParser()
    blocks = []
    for i, text in enumerate(ref_texts):
        blocks.append(Block(
            block_id=f"mock_blk_{i}",
            text=text,
            index=i,
            block_type=BlockType.REFERENCE_ENTRY
        ))
    
    from app.models.document import PipelineDocument
    doc_obj = PipelineDocument(document_id="ref_test", filename="refs.docx", blocks=blocks)
    doc_obj = parser.process(doc_obj)
    
    print(f"✅ Parsed {len(doc_obj.references)} references.")
    for ref in doc_obj.references:
        print(f"  - [{ref.citation_key}] {ref.title} ({ref.year})")

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_reference_detection.py <docx_path>")
        print("(Running mock tests only if no path provided)")
    
    input_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "12_references.json"
    
    print("=" * 70)
    print("NORMAL TEST: REFERENCE DETECTION")
    print("=" * 70)
    
    # 1. Run Mock Test
    test_mock_references()

    # 2. Run on actual file if provided
    blocks = []
    refs = []
    if input_path:
        print(f"\n[Case 2] Running on target: {input_path}")
        parser = DocxParser()
        ref_parser = ReferenceParser()
        doc_obj = parser.parse(input_path, "active_test")
        doc_obj = ref_parser.process(doc_obj)
        blocks = doc_obj.blocks
        refs = doc_obj.references
        print(f"✅ Parsed {len(refs)} references from file.")

    # 3. Save Output
    print("\n[3/3] Saving results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_reference_blocks": len([b for b in blocks if b.block_type == BlockType.REFERENCE_ENTRY]),
                "extracted_references": len(refs)
            },
            "references": [ref.model_dump() for ref in refs]
        }, f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Ref Blocks Detected: {len([b for b in blocks if b.block_type == BlockType.REFERENCE_ENTRY])}")
    print(f"Extracted Refs:      {len(refs)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
