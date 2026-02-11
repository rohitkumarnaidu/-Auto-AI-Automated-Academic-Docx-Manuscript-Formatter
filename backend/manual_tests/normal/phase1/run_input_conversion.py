"""
Normal Test: Stage 1 Input Conversion (Parsing)
Purpose: Verify DOCX parsing and block extraction, save to JSON
Input: DOCX file
Output: manual_tests/outputs/01_blocks.json
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_input_conversion.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "01_blocks.json"
    
    print("=" * 70)
    print("NORMAL TEST: INPUT CONVERSION (PARSING)")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/2] Parsing DOCX...")
    parser = DocxParser()
    doc_obj = parser.parse(input_path, "test_job_parse")
    
    # Analysis
    blocks = doc_obj.blocks
    
    # Save Output
    print("[2/2] Saving block results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_blocks": len(blocks),
                "has_figures": len(doc_obj.figures) > 0,
                "has_tables": len(doc_obj.tables) > 0
            },
            "blocks": [b.model_dump() for b in blocks]
        }, f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Total Blocks: {len(blocks)}")
    print(f"Figures:      {len(doc_obj.figures)}")
    print(f"Tables:       {len(doc_obj.tables)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
