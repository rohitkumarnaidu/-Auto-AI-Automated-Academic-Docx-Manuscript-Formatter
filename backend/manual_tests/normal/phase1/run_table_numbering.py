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
    print(f"\n🚀 PHASE 1: TABLE NUMBERING")
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
    
    # Apply numbering
    tables = doc.tables
    for i, tab in enumerate(tables, 1):
        tab.number = i
        tab.metadata["table_number"] = i
    
    # 2. Analysis
    numbers = [t.metadata.get('table_number') for t in tables if t.metadata.get('table_number')]
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "10_table_numbering.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "tables_numbered": len(tables),
                "sequence": numbers
            },
            "tables": [
                {
                    "table_id": t.table_id,
                    "number": t.number,
                    "caption_block_id": t.caption_block_id
                }
                for t in tables
            ]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Tables Numbered: {len(tables)}")
    print(f"Sequence: {numbers}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_table_numbering.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
