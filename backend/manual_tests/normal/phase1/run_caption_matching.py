"""
Normal Test: Figure Caption Matching
Purpose: Verify figure caption matching logic and save to JSON
Input: DOCX file
Output: manual_tests/outputs/05_caption_matching.json
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
from app.pipeline.figures.caption_matcher import CaptionMatcher

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_caption_matching.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "05_caption_matching.json"
    
    print("=" * 70)
    print("NORMAL TEST: FIGURE CAPTION MATCHING")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/4] Parsing & Normalizing...")
    parser = DocxParser()
    normalizer = Normalizer()
    doc_obj = parser.parse(input_path, "test_job_fcm")
    doc_obj = normalizer.process(doc_obj)
    
    print("[2/4] Structure & Classification...")
    detector = StructureDetector()
    classifier = ContentClassifier()
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    
    print("[3/4] Caption Matching (Figures)...")
    matcher = CaptionMatcher()
    doc_obj = matcher.process(doc_obj)
    
    # Analysis
    matched = [f for f in doc_obj.figures if f.caption_block_id]
    
    # Save Output
    print("[4/4] Saving results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_figures": len(doc_obj.figures),
                "matched_captions": len(matched)
            },
            "figures": [
                {
                    "figure_id": f.figure_id,
                    "caption_block_id": f.caption_block_id,
                    "anchor_index": f.metadata.get("anchor_index")
                }
                for f in doc_obj.figures
            ]
        }, f, indent=2)
    
    print(f"\n--- Results Summary ---")
    print(f"Total Figures:   {len(doc_obj.figures)}")
    print(f"Matched Captions:{len(matched)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
