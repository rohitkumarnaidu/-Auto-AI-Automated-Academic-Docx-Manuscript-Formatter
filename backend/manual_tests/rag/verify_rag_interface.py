import sys
import os

# Set up path to import app modules
sys.path.append(os.path.abspath("."))

from app.pipeline.intelligence.rag_engine import get_rag_engine

def test_rag_interface():
    print("Initializing RagEngine singleton...")
    rag = get_rag_engine()
    
    print("\nTesting 'query_rules' method...")
    try:
        # Test with IEEE Introduction
        results = rag.query_rules("IEEE", "Introduction", top_k=2)
        print(f"SUCCESS: 'query_rules' exists. Results returned: {len(results)}")
        for i, r in enumerate(results):
            print(f" - Rule {i+1}: {str(r)[:100]}...")
            if not isinstance(r, dict) or "text" not in r:
                print(f"WARNING: Result {i} does not match expected dict structure.")
    except AttributeError:
        print("FAILURE: 'query_rules' NOT found.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR during 'query_rules': {e}")
        # Note: We expect it to succeed even if ChromaDB is missing (using native fallback)
        sys.exit(1)

    print("\nTesting 'query_guidelines' method...")
    try:
        results = rag.query_guidelines("IEEE", "Introduction", top_k=2)
        print(f"SUCCESS: 'query_guidelines' exists. Results returned: {len(results)}")
    except AttributeError:
        print("FAILURE: 'query_guidelines' NOT found.")
        sys.exit(1)

    print("\nInterface verification complete.")

if __name__ == "__main__":
    test_rag_interface()
