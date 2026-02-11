import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.tables.inserter import TableInserter
from app.models import BlockType

def main(input_path):
    print(f"\n🚀 PHASE 1: TABLE INSERTION (ANCHORS)")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    classifier = ContentClassifier()
    inserter = TableInserter()
    
    blocks = parser.parse_docx(input_path)
    blocks = detector.detect_structure(blocks)
    blocks = classifier.classify_blocks(blocks)
    tables = [b for b in blocks if b.type == BlockType.TABLE]
    tables_with_anchors = inserter.find_insertion_points(blocks, tables)
    
    # 2. Analysis
    anchor_indices = [t.metadata.get('anchor_index') for t in tables_with_anchors if t.metadata.get('anchor_index') is not None]
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "11_table_insertion.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "insertion_points_found": len(anchor_indices)
            },
            "tables": [b.model_dump() for b in tables_with_anchors]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Anchors Found: {len(anchor_indices)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_table_insertion.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
