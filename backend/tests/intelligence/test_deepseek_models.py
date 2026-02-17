"""
DeepSeek Model Comparison Test
Compares deepseek-r1:8b vs deepseek-r1:0b for semantic reasoning quality.
"""

import sys
import time
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.pipeline.intelligence.reasoning_engine import ReasoningEngine

def test_model_comparison():
    """Compare deepseek-r1:8b vs deepseek-r1:0b"""
    
    print("="*60)
    print("DEEPSEEK MODEL COMPARISON TEST")
    print("="*60)
    
    models = ["deepseek-r1:8b", "deepseek-r1:0b"]
    
    # Test data
    test_blocks = [
        {"text": "Introduction", "index": 0, "block_id": "b1"},
        {"text": "This paper presents a novel approach to academic manuscript formatting using AI-powered semantic analysis.", "index": 1, "block_id": "b2"},
        {"text": "Methodology", "index": 2, "block_id": "b3"},
        {"text": "We employed a multi-stage pipeline consisting of extraction, classification, and formatting layers.", "index": 3, "block_id": "b4"}
    ]
    
    rules = """
    Academic paper formatting guidelines:
    - Headings should be identified by semantic importance
    - Abstract sections require special handling
    - References must be formatted according to citation style
    - Figures and tables need sequential numbering
    """
    
    results = {}
    
    for model in models:
        print(f"\n{'='*60}")
        print(f"Testing: {model}")
        print(f"{'='*60}")
        
        try:
            engine = ReasoningEngine(model=model)
            
            # Test 1: Latency
            start = time.time()
            output = engine.generate_instruction_set(test_blocks, rules)
            latency = time.time() - start
            
            # Test 2: Success
            success = "error" not in output
            
            # Test 3: Output quality
            if success:
                num_blocks = len(output.get("blocks", []))
                has_confidence = all("confidence" in b for b in output.get("blocks", []))
                has_semantic_type = all("semantic_type" in b for b in output.get("blocks", []))
            else:
                num_blocks = 0
                has_confidence = False
                has_semantic_type = False
            
            results[model] = {
                "latency": latency,
                "success": success,
                "num_blocks": num_blocks,
                "has_confidence": has_confidence,
                "has_semantic_type": has_semantic_type,
                "output": output
            }
            
            print(f"✅ Latency: {latency:.2f}s")
            print(f"✅ Success: {success}")
            print(f"✅ Blocks processed: {num_blocks}")
            print(f"✅ Has confidence scores: {has_confidence}")
            print(f"✅ Has semantic types: {has_semantic_type}")
            
            if success:
                print(f"\nSample output:")
                print(json.dumps(output, indent=2)[:500] + "...")
            
        except Exception as e:
            print(f"❌ Error testing {model}: {e}")
            results[model] = {
                "latency": 0,
                "success": False,
                "error": str(e)
            }
    
    # Comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    if len(results) == 2:
        model1, model2 = models
        r1, r2 = results[model1], results[model2]
        
        print(f"\n{'Metric':<30} {model1:<20} {model2:<20}")
        print("-"*70)
        print(f"{'Latency':<30} {r1['latency']:.2f}s{'':<14} {r2['latency']:.2f}s")
        print(f"{'Success':<30} {r1['success']}{'':<15} {r2['success']}")
        print(f"{'Blocks Processed':<30} {r1.get('num_blocks', 0)}{'':<16} {r2.get('num_blocks', 0)}")
        print(f"{'Has Confidence':<30} {r1.get('has_confidence', False)}{'':<15} {r2.get('has_confidence', False)}")
        print(f"{'Has Semantic Types':<30} {r1.get('has_semantic_type', False)}{'':<15} {r2.get('has_semantic_type', False)}")
        
        # Recommendation
        print("\n" + "="*60)
        print("RECOMMENDATION")
        print("="*60)
        
        if r1['success'] and r2['success']:
            if r2['latency'] < r1['latency'] and r2.get('num_blocks') == r1.get('num_blocks'):
                print(f"✅ {model2} is FASTER with same quality")
                print(f"   Speedup: {((r1['latency'] - r2['latency']) / r1['latency'] * 100):.1f}%")
            elif r1['latency'] < r2['latency']:
                print(f"✅ {model1} is faster")
            else:
                print("⚖️  Similar performance - choose based on accuracy testing")
        elif r1['success']:
            print(f"✅ {model1} is more reliable")
        elif r2['success']:
            print(f"✅ {model2} is more reliable")
        else:
            print("❌ Both models failed - check Ollama server")
    
    return results

if __name__ == "__main__":
    print("\n🔬 Starting DeepSeek Model Comparison...\n")
    
    # Check if Ollama is running
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            models = response.json().get("models", [])
            print(f"   Available models: {[m['name'] for m in models]}")
        else:
            print("⚠️  Ollama server responded but with error")
    except:
        print("❌ Ollama server not reachable at localhost:11434")
        print("   Please start Ollama: ollama serve")
        sys.exit(1)
    
    # Run comparison
    results = test_model_comparison()
    
    print("\n✅ Test complete!")
    print("\nNext steps:")
    print("1. Review comparison results above")
    print("2. Test with real documents for accuracy")
    print("3. Update reasoning_engine.py with chosen model")
