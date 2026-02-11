import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer
from app.pipeline.structure_detection.detector import StructureDetector

def main(input_path):
    print(f"\n🚀 PHASE 1: STRUCTURE DETECTION")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return
    
    # 1. Pipeline Execution
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    
    doc = parser.parse(input_path, "test_job")
    doc = normalizer.process(doc)
    doc = detector.process(doc)
    
    # 2. Analysis
    blocks = doc.blocks
    headings = [b for b in blocks if b.metadata.get("is_heading_candidate")]
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "02_structure.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_blocks": len(blocks),
                "headings_detected": len(headings),
                "heading_levels": {
                    f"L{i}": len([h for h in headings if h.metadata.get("level") == i])
                    for i in range(1, 5)
                }
            },
            "headings": [
                {
                    "text": h.text,
                    "level": h.metadata.get("level"),
                    "confidence": h.metadata.get("heading_confidence"),
                    "index": h.index
                }
                for h in headings
            ]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Total Blocks: {len(blocks)}")
    print(f"Headings Detected: {len(headings)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_structure.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
