import sys
import os

# Set up path to import app modules
sys.path.append(os.path.abspath("."))

from app.pipeline.intelligence.semantic_parser import get_semantic_parser
from app.models import Block, BlockType

def test_interface():
    print("Initializing SemanticParser singleton...")
    parser = get_semantic_parser()
    
    # Test blocks
    blocks = [
        Block(block_id="1", index=0, text="2", block_type=BlockType.UNKNOWN),
        Block(block_id="2", index=1, text="ethodology", block_type=BlockType.UNKNOWN),
        Block(block_id="3", index=2, text="This is a body paragraph.", block_type=BlockType.BODY)
    ]
    
    print("\nTesting 'detect_boundaries' method...")
    try:
        repaired = parser.detect_boundaries(blocks)
        print(f"SUCCESS: 'detect_boundaries' exists. Blocks after repair: {len(repaired)}")
        for b in repaired:
            print(f" - [{b.block_type}] {b.text}")
    except AttributeError:
        print("FAILURE: 'detect_boundaries' NOT found.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR during 'detect_boundaries': {e}")
        sys.exit(1)

    print("\nTesting 'reconcile_fragmented_headings' method...")
    try:
        reconciled = parser.reconcile_fragmented_headings(blocks)
        print(f"SUCCESS: 'reconcile_fragmented_headings' exists.")
    except AttributeError:
        print("FAILURE: 'reconcile_fragmented_headings' NOT found.")
        sys.exit(1)

    print("\nInterface verification complete.")

if __name__ == "__main__":
    test_interface()
