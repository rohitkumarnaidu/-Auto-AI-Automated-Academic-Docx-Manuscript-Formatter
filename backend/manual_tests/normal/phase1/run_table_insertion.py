import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.tables.caption_matcher import TableCaptionMatcher

def main(input_path):
    print(f"\n🚀 PHASE 1: TABLE INSERTION")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = TableCaptionMatcher()
    
    doc = parser.parse(input_path, "test_job")
    doc = normalizer.process(doc)
    doc = detector.process(doc)
    doc = classifier.process(doc)
    doc = matcher.process(doc)
    
    # Apply numbering and find insertion points
    tables = doc.tables
    blocks = doc.blocks
    
    for i, tab in enumerate(tables, 1):
        tab.number = i
        tab.metadata["table_number"] = i
        
        # Find insertion point (after caption)
        if tab.caption_block_id:
            caption_block = next((b for b in blocks if b.block_id == tab.caption_block_id), None)
            if caption_block:
                tab.metadata["anchor_index"] = caption_block.index + 1
    
    # 2. Analysis
    anchors_found = len([t for t in tables if "anchor_index" in t.metadata])
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "11_table_insertion.json"
    
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
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Total Tables: {len(tables)}")
    print(f"Anchors Found: {anchors_found}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_table_insertion.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
