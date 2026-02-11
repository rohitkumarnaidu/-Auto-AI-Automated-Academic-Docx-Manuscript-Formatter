"""
Normal Test: Table Extraction
Purpose: Verify table cell-level extraction and save to JSON
Input: DOCX file
Output: manual_tests/outputs/08_tables.json
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
        print("Usage: python run_table_extraction.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "08_tables.json"
    
    print("=" * 70)
    print("NORMAL TEST: TABLE EXTRACTION")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Running Pipeline stages...")
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    
    doc_obj = parser.parse(input_path, "test_job_tabext")
    doc_obj = normalizer.process(doc_obj)
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    
    # Analysis
    tables = doc_obj.tables
    
    # Save Output
    print("[2/3] Saving table results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "tables_detected": len(tables)
            },
            "tables": [tab.model_dump() for tab in tables]
        }, f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Tables Detected: {len(tables)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
