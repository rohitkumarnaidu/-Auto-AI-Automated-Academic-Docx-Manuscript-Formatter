import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser

def main(input_path):
    print(f"\n🚀 PHASE 1: INPUT CONVERSION (PARSING)")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return
    
    # 1. Pipeline Execution
    parser = DocxParser()
    doc = parser.parse(input_path, "test_job")
    
    # 2. Analysis
    blocks = doc.blocks
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "01_blocks.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_blocks": len(blocks),
                "has_figures": len(doc.figures) > 0,
                "has_tables": len(doc.tables) > 0
            },
            "blocks": [b.model_dump() for b in blocks]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Total Blocks: {len(blocks)}")
    print(f"Figures: {len(doc.figures)}")
    print(f"Tables: {len(doc.tables)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_input_conversion.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
