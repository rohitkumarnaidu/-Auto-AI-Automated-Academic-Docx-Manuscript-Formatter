"""
Manual test for NLP logic.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.pipeline.nlp.analyzer import ContentAnalyzer
from app.models import Document, Block, BlockType

def test_nlp():
    print("\n" + "=" * 70)
    print("NLP ENRICHMENT MANUAL TEST")
    print("=" * 70)
    
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
    
    print("[1] Running Analysis (spacy optional warning likely)...")
    doc = analyzer.analyze(doc)
    
    print("\n[2] Checking Hints...")
    
    # Check Section Confidence
    b1_hints = doc.blocks[0].metadata.get("ai_hints", {})
    if b1_hints.get("predicted_section") == "Abstract":
        print(f"✅ Block 0: Detected Abstract ({b1_hints['confidence']})")
    else:
        print(f"❌ Block 0: Failed detection. Hints: {b1_hints}")

    # Check Readability
    b2_hints = doc.blocks[1].metadata.get("ai_hints", {})
    if "readability" in b2_hints:
        print(f"✅ Block 1: Readability assessed: {b2_hints['readability']}")
    else:
        print(f"❌ Block 1: Missing readability. Hints: {b2_hints}")
        
    # Check Caption Quality
    b3_hints = doc.blocks[2].metadata.get("ai_hints", {})
    if b3_hints.get("caption_quality") == "Good":
        print(f"✅ Block 2: Good caption detected")
    
    b4_hints = doc.blocks[3].metadata.get("ai_hints", {})
    if b4_hints.get("caption_quality") == "Possibly Vague":
         print(f"✅ Block 3: Vague caption detected")
    else:
         print(f"❌ Block 3: Vague check failed. Got: {b4_hints.get('caption_quality')}")

    # Check Introduction
    b5_hints = doc.blocks[4].metadata.get("ai_hints", {})
    if b5_hints.get("predicted_section") == "Introduction":
        print(f"✅ Block 4: Introduction detected")
    else:
        print(f"❌ Block 4: Failed Intro detection. Hints: {b5_hints}")

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETE")

if __name__ == "__main__":
    test_nlp()
