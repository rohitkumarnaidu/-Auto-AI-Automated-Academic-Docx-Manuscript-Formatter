"""
Manual test script for full pipeline assembly.

Tests: Complete pipeline execution from parsing to assembly
Output: 09_pipeline_document.json
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase2)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer as TextNormalizer
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.pipeline.tables.caption_matcher import TableCaptionMatcher

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "09_pipeline_document.json"
    
    print("=" * 70)
    print("FULL PIPELINE ASSEMBLY TEST")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print()
    
    # Stage 1: Parse
    print("[1/6] Parsing DOCX...")
    parser = DocxParser()
    doc_obj = parser.parse(input_path, document_id="pipeline_test")
    print(f"  ✓ Extracted {len(doc_obj.blocks)} blocks")
    print(f"  ✓ Extracted {len(doc_obj.figures)} figures")
    print(f"  ✓ Extracted {len(doc_obj.tables)} tables")
    
    # Stage 2: Normalize
    print("[2/6] Normalizing text...")
    normalizer = TextNormalizer()
    doc_obj = normalizer.process(doc_obj)
    print(f"  ✓ Normalized to {len(doc_obj.blocks)} blocks")
    
    # Stage 3: Structure Detection
    print("[3/6] Detecting structure...")
    detector = StructureDetector()
    doc_obj = detector.process(doc_obj)
    heading_count = sum(1 for b in doc_obj.blocks if b.metadata.get('is_heading_candidate', False))
    print(f"  ✓ Detected {heading_count} headings")
    
    # Stage 4: Classification
    print("[4/6] Classifying blocks...")
    classifier = ContentClassifier()
    doc_obj = classifier.process(doc_obj)
    type_counts = {}
    for b in doc_obj.blocks:
        type_counts[b.block_type.value] = type_counts.get(b.block_type.value, 0) + 1
    print(f"  ✓ Classified {len(doc_obj.blocks)} blocks into {len(type_counts)} types")
    
    # Stage 5: Caption Matching
    print("[5/6] Matching captions...")
    fig_matcher = CaptionMatcher()
    tab_matcher = TableCaptionMatcher()
    doc_obj = fig_matcher.process(doc_obj)
    doc_obj = tab_matcher.process(doc_obj)
    
    fig_matched = sum(1 for f in doc_obj.figures if f.caption_block_id)
    tab_matched = sum(1 for t in doc_obj.tables if t.caption_block_id)
    print(f"  ✓ Matched {fig_matched}/{len(doc_obj.figures)} figure captions")
    print(f"  ✓ Matched {tab_matched}/{len(doc_obj.tables)} table captions")
    
    # Stage 6: Save assembled document
    print("[6/6] Saving assembled document...")
    
    # Serialize to JSON
    output_data = {
        "document_id": doc_obj.document_id,
        "original_filename": doc_obj.original_filename,
        "blocks": [
            {
                "block_id": b.block_id,
                "index": b.index,
                "text": b.text[:100] + "..." if len(b.text) > 100 else b.text,
                "block_type": b.block_type.value,
                "section_name": b.section_name
            }
            for b in doc_obj.blocks
        ],
        "figures": [
            {
                "figure_id": f.figure_id,
                "caption_text": f.caption_text,
                "caption_block_id": f.caption_block_id,
                "number": f.number,
                "metadata": {"block_index": f.metadata.get("block_index")}
            }
            for f in doc_obj.figures
        ],
        "tables": [
            {
                "table_id": t.table_id,
                "block_index": t.block_index,
                "caption_text": t.caption_text,
                "caption_block_id": t.caption_block_id,
                "number": t.number,
                "num_rows": t.num_rows,
                "num_cols": t.num_cols
            }
            for t in doc_obj.tables
        ],
        "references": [
            {
                "reference_id": r.reference_id,
                "citation_key": r.citation_key,
                "raw_text": r.raw_text[:100] + "..." if len(r.raw_text) > 100 else r.raw_text
            }
            for r in doc_obj.references
        ],
        "summary": {
            "total_blocks": len(doc_obj.blocks),
            "total_figures": len(doc_obj.figures),
            "total_tables": len(doc_obj.tables),
            "total_references": len(doc_obj.references),
            "block_types": type_counts
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Saved to {output_path}")
    
    print()
    print("=" * 70)
    print("✓ PIPELINE ASSEMBLY COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  Blocks: {len(doc_obj.blocks)}")
    print(f"  Figures: {len(doc_obj.figures)} ({fig_matched} with captions)")
    print(f"  Tables: {len(doc_obj.tables)} ({tab_matched} with captions)")
    print(f"  References: {len(doc_obj.references)}")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ PIPELINE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
