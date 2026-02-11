import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.nlp.analyzer import ContentAnalyzer
from app.models import Document, Block, BlockType

def main():
    print(f"\n🚀 PHASE 1: NLP ENRICHMENT DEBUG")
    
    analyzer = ContentAnalyzer()
    
    # Create Mock Document
    doc = Document(document_id="test_nlp", original_filename="nlp.docx")
    doc.blocks = [
        # Abstract candidate
        Block(block_id="b1", text="Abstract", block_type=BlockType.UNKNOWN, index=0),
        Block(block_id="b2", text="This paper presents results. Background is distinct.", block_type=BlockType.ABSTRACT_BODY, index=1),
        
        # Caption candidate (Good)
        Block(block_id="b3", text="Figure 1: Performance comparison of methods.", block_type=BlockType.FIGURE_CAPTION, index=2),
        
        # Caption candidate (Vague)
        Block(block_id="b4", text="Figure 2: Chart below.", block_type=BlockType.FIGURE_CAPTION, index=3),
        
        # Header candidate
        Block(block_id="b5", text="1. Introduction", block_type=BlockType.UNKNOWN, index=4)
    ]
    
    print("[1] Running Analysis...")
    try:
        doc = analyzer.analyze(doc)
    except Exception as e:
        print(f"❌ NLP Analysis Error: {e}")
        return

    print("\n[2] Checking AI Hints...")
    
    # Verification Results
    results = []
    
    # Abstract
    b1_hints = doc.blocks[0].metadata.get("ai_hints", {})
    if b1_hints.get("predicted_section") == "Abstract":
        print(f"✅ Block 0: Detected Abstract ({b1_hints.get('confidence')})")
        results.append("Abstract OK")

    # Readability
    b2_hints = doc.blocks[1].metadata.get("ai_hints", {})
    if "readability" in b2_hints:
        print(f"✅ Block 1: Readability assessed: {b2_hints['readability']}")
        results.append("Readability OK")

    # Caption Quality
    b3_hints = doc.blocks[2].metadata.get("ai_hints", {})
    if b3_hints.get("caption_quality") == "Good":
        print(f"✅ Block 2: Good caption detected")
        results.append("Caption Quality OK")
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "13_nlp_debug.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(doc.model_dump(), f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Tests Passed: {len(results)}/3")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
