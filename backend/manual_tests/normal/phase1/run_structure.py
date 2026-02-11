"""
Normal Test: Structure Detection
Purpose: Verify heading detection, level analysis, and confidence scores
Input: DOCX file
Output: manual_tests/outputs/02_structure.json
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_structure.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "02_structure.json"
    
    print("=" * 70)
    print("NORMAL TEST: STRUCTURE DETECTION")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Parsing & Normalizing...")
    parser = DocxParser()
    normalizer = Normalizer()
    doc_obj = parser.parse(input_path, "test_job_struct")
    doc_obj = normalizer.process(doc_obj)
    
    print("[2/3] Structure Detection...")
    detector = StructureDetector()
    doc_obj = detector.process(doc_obj)
    
    # Analysis
    headings = [b for b in doc_obj.blocks if b.metadata.get("is_heading_candidate")]
    
    # Save Output
    print("[3/3] Saving structure results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_blocks": len(doc_obj.blocks),
                "headings_detected": len(headings),
                "heading_levels": {
                    f"L{i}": len([h for h in headings if h.metadata.get("level") == i])
                    for i in range(1, 10)
                }
            },
            "headings": [
                {
                    "text": h.text,
                    "level": h.metadata.get("level"),
                    "confidence": h.metadata.get("heading_confidence"),
                    "index": h.index,
                    "reasons": h.metadata.get("reasons", [])
                }
                for h in headings
            ]
        }, f, indent=2)
    
    print(f"\n--- Results Summary ---")
    print(f"Total Blocks:      {len(doc_obj.blocks)}")
    print(f"Headings Detected: {len(headings)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
