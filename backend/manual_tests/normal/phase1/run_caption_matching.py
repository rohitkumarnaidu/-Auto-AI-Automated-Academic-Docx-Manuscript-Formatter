import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.models import BlockType

def main(input_path):
    print(f"\n🚀 PHASE 1: FIGURE CAPTION MATCHING")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = CaptionMatcher()
    
    blocks = parser.parse_docx(input_path)
    blocks = detector.detect_structure(blocks)
    blocks = classifier.classify_blocks(blocks)
    # Match captions
    figures = matcher.match_captions(blocks)
    
    # 2. Analysis
    matched_count = sum(1 for f in figures if f.metadata.get('caption'))
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "05_caption_matching.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "figures_with_captions": matched_count
            },
            "figures": [b.model_dump() for b in figures]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Matched Figures:  {matched_count}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_caption_matching.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
