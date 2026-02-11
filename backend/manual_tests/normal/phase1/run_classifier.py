"""
Normal Test: Content Classification
Purpose: Verify block-level semantic classification and save to JSON
Input: DOCX file
Output: manual_tests/outputs/03_classified.json
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_classifier.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "03_classified.json"
    
    print("=" * 70)
    print("NORMAL TEST: CONTENT CLASSIFICATION")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/4] Parsing & Normalizing...")
    parser = DocxParser()
    normalizer = Normalizer()
    doc_obj = parser.parse(input_path, "test_job_cls")
    doc_obj = normalizer.process(doc_obj)
    
    print("[2/4] Structure Detection...")
    detector = StructureDetector()
    doc_obj = detector.process(doc_obj)
    
    print("[3/4] Content Classification...")
    classifier = ContentClassifier()
    doc_obj = classifier.process(doc_obj)
    
    # Analysis
    type_counts = {}
    for b in doc_obj.blocks:
        bt = b.block_type.value if hasattr(b.block_type, 'value') else str(b.block_type)
        type_counts[bt] = type_counts.get(bt, 0) + 1
    
    # Save Output
    print("[4/4] Saving results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_blocks": len(doc_obj.blocks),
                "type_distribution": type_counts
            },
            "blocks": [
                {
                    "index": b.index,
                    "text": b.text[:100],
                    "block_type": b.block_type.value if hasattr(b.block_type, 'value') else str(b.block_type),
                    "confidence": b.classification_confidence
                }
                for b in doc_obj.blocks
            ]
        }, f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Total Blocks: {len(doc_obj.blocks)}")
    print(f"Type Distribution:")
    for bt, count in sorted(type_counts.items()):
        print(f"  {bt:.<20} {count}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
