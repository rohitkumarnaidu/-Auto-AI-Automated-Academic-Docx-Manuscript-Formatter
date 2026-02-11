import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import all models
from app.models import (
    Block, BlockType, TextStyle,
    Figure, ImageFormat,
    Table, TableCell,
    Reference, ReferenceType,
    Document, DocumentMetadata, TemplateInfo
)

def test_block_model():
    print("\n[1] Testing Block Model...")
    block = Block(
        block_id="blk_001",
        text="This is a test paragraph.",
        index=0,
        block_type=BlockType.PARAGRAPH
    )
    print(f"✅ Created block: {block.block_id}")
    return block

def test_document_serialization():
    print("\n[2] Testing JSON Serialization...")
    block = Block(block_id="blk_test", text="Test", index=0)
    doc = Document(document_id="doc_test", blocks=[block])
    
    json_data = doc.model_dump_json()
    doc_restored = Document.model_validate_json(json_data)
    
    if doc_restored.document_id == "doc_test":
        print("✅ Serialization/Deserialization successful.")
    else:
        print("❌ Data mismatch in restoral.")

def main():
    print(f"\n🚀 PHASE 1: DOMAIN MODEL VALIDATION")
    
    try:
        test_block_model()
        test_document_serialization()
        
        print("\n✅ ALL MODELS FUNCTIONAL")
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
