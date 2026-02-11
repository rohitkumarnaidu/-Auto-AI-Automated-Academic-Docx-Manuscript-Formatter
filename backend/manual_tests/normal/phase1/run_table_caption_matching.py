"""
Normal Test: Table Caption Matching
Purpose: Verify table caption matching logic and save to JSON
Input: DOCX file
Output: manual_tests/outputs/09_table_caption_matching.json
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
from app.pipeline.tables.caption_matcher import TableCaptionMatcher

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_table_caption_matching.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "09_table_caption_matching.json"
    
    print("=" * 70)
    print("NORMAL TEST: TABLE CAPTION MATCHING")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/4] Parsing & Normalizing...")
    parser = DocxParser()
    normalizer = Normalizer()
    doc_obj = parser.parse(input_path, "test_job_tcm")
    doc_obj = normalizer.process(doc_obj)
    
    print("[2/4] Structure & Classification...")
    detector = StructureDetector()
    classifier = ContentClassifier()
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    
    print("[3/4] Caption Matching (Tables)...")
    matcher = TableCaptionMatcher()
    doc_obj = matcher.process(doc_obj)
    
    # Analysis
    matched = [t for t in doc_obj.tables if t.caption_block_id]
    
    # Save Output
    print("[4/4] Saving results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_tables": len(doc_obj.tables),
                "matched_captions": len(matched)
            },
            "tables": [
                {
                    "table_id": t.table_id,
                    "caption_block_id": t.caption_block_id,
                    "anchor_index": t.metadata.get("anchor_index")
                }
                for t in doc_obj.tables
            ]
        }, f, indent=2)
    
    print(f"\n--- Results Summary ---")
    print(f"Total Tables:    {len(doc_obj.tables)}")
    print(f"Matched Captions:{len(matched)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
