"""
Normal Test: NLP Enrichment Debug
Purpose: Verify NLP analysis (AI hints, readability, quality) with mock data
Input: N/A (Mocked)
Output: manual_tests/outputs/13_nlp_debug.json
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.nlp.analyzer import ContentAnalyzer
from app.models.document import PipelineDocument
from app.models.block import Block, BlockType

def main():
    print("=" * 70)
    print("NORMAL TEST: NLP ENRICHMENT DEBUG")
    print("=" * 70)
    
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "13_nlp_debug.json"
    
    analyzer = ContentAnalyzer()
    
    # Create Mock Document
    print("[1/3] Creating Mock Document...")
    doc_obj = PipelineDocument(document_id="test_nlp", filename="nlp.docx")
    doc_obj.blocks = [
        # Abstract candidate
        Block(block_id="b1", text="Abstract", block_type=BlockType.UNKNOWN, index=0),
        Block(block_id="b2", text="This paper presents results. Background is distinct.", block_type=BlockType.ABSTRACT_BODY, index=1),
        
        # Caption candidate (Good)
        Block(block_id="b3", text="Figure 1: Performance comparison of methods.", block_type=Block_TYPE_FIGURE_CAPTION, index=2),
        
        # Caption candidate (Vague)
        Block(block_id="b4", text="Figure 2: Chart below.", block_type=Block_TYPE_FIGURE_CAPTION, index=3),
        
        # Header candidate
        Block(block_id="b5", text="1. Introduction", block_type=BlockType.UNKNOWN, index=4)
    ]
    
    print("[2/3] Running NLP Analysis Toolchain...")
    try:
        doc_obj = analyzer.process(doc_obj)
    except Exception as e:
        print(f"❌ NLP Analysis Error: {e}")
        return

    # Verification Results
    print("[3/3] Saving results...")
    results = []
    
    # Abstract
    b1_hints = doc_obj.blocks[0].metadata.get("ai_hints", {})
    if b1_hints.get("predicted_section") == "Abstract":
        results.append("Abstract OK")

    # Readability
    b2_hints = doc_obj.blocks[1].metadata.get("ai_hints", {})
    if "readability" in b2_hints:
        results.append("Readability OK")

    # Caption Quality
    b3_hints = doc_obj.blocks[2].metadata.get("ai_hints", {})
    if b3_hints.get("caption_quality") == "Good":
        results.append("Caption Quality OK")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(doc_obj.model_dump(), f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Tests Passed: {len(results)}/3")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
