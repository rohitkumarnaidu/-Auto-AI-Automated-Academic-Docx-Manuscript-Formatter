"""
Normal Test: Domain Model Validation
Purpose: Verify core data models and serialization logic
Input: N/A (Internal validation)
Output: Console Output
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend to path (Depth 3)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import all models
from app.models.block import Block, BlockType
from app.models import PipelineDocument

def test_block_model():
    print("\n[1/3] Testing Block Model...")
    block = Block(
        block_id="blk_001",
        text="This is a test paragraph.",
        index=0,
        block_type=BlockType.PARAGRAPH
    )
    print(f"✅ Created block: {block.block_id}")
    return block

def test_document_serialization():
    print("\n[2/3] Testing JSON Serialization...")
    block = Block(block_id="blk_test", text="Test", index=0)
    doc_obj = PipelineDocument(document_id="doc_test", filename="test.docx", blocks=[block])
    
    json_data = doc_obj.model_dump_json()
    doc_restored = PipelineDocument.model_validate_json(json_data)
    
    if doc_restored.document_id == "doc_test":
        print("✅ Serialization/Deserialization successful.")
    else:
        print(f"❌ Data mismatch in restoral: {doc_restored.document_id}")
        sys.exit(1)

def main():
    print("=" * 70)
    print("NORMAL TEST: DOMAIN MODEL VALIDATION")
    print("=" * 70)
    
    try:
        test_block_model()
        test_document_serialization()
        
        print("\n[3/3] Finalizing results...")
        print("✅ SUCCESS: ALL MODELS FUNCTIONAL")
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
