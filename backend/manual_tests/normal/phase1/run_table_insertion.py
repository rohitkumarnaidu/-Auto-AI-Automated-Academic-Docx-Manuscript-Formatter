"""
Normal Test: Table Insertion
Purpose: Verify anchor detection logic for table insertion and save to JSON
Input: DOCX file
Output: manual_tests/outputs/11_table_insertion.json
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
        print("Usage: python run_table_insertion.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "11_table_insertion.json"
    
    print("=" * 70)
    print("NORMAL TEST: TABLE INSERTION")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Running Pipeline stages...")
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = TableCaptionMatcher()
    
    doc_obj = parser.parse(input_path, "test_job_tabins")
    doc_obj = normalizer.process(doc_obj)
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    doc_obj = matcher.process(doc_obj)
    
    # Simple anchor logic
    tables = doc_obj.tables
    blocks = doc_obj.blocks
    anchors_found = 0
    
    for i, tab in enumerate(tables, 1):
        tab.number = i
        if tab.caption_block_id:
            caption_block = next((b for b in blocks if b.block_id == tab.caption_block_id), None)
            if caption_block:
                tab.metadata["anchor_index"] = caption_block.index + 1
                anchors_found += 1
    
    # Save Output
    print("[2/3] Saving insertion results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_tables": len(tables),
                "anchors_found": anchors_found
            },
            "tables": [
                {
                    "table_id": t.table_id,
                    "number": t.number,
                    "caption_block_id": t.caption_block_id,
                    "anchor_index": t.metadata.get("anchor_index")
                }
                for t in tables
            ]
        }, f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Total Tables:    {len(tables)}")
    print(f"Anchors Found:   {anchors_found}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
