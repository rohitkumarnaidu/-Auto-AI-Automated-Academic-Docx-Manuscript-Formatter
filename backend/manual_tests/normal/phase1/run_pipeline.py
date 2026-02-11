"""
Normal Test: End-to-End Pipeline
Purpose: Verify the entire pipeline from parsing to validation and save audit log
Input: DOCX file
Output: manual_tests/outputs/pipeline_audit.json
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.pipeline.tables.caption_matcher import TableCaptionMatcher
from app.pipeline.references.parser import ReferenceParser
from app.pipeline.validation.validator import DocumentValidator

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "pipeline_audit.json"
    
    print("=" * 70)
    print("NORMAL TEST: END-TO-END PIPELINE")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Running End-to-End Pipeline...")
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    fig_matcher = CaptionMatcher()
    tab_matcher = TableCaptionMatcher()
    ref_parser = ReferenceParser()
    validator = DocumentValidator()
    
    doc_obj = parser.parse(input_path, "test_job_full")
    doc_obj = normalizer.process(doc_obj)
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    doc_obj = fig_matcher.process(doc_obj)
    doc_obj = tab_matcher.process(doc_obj)
    doc_obj = ref_parser.process(doc_obj)
    doc_obj = validator.process(doc_obj)
    
    # Save Output
    print("[2/3] Saving audit results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_blocks": len(doc_obj.blocks),
                "figures": len(doc_obj.figures),
                "tables": len(doc_obj.tables),
                "is_valid": doc_obj.is_valid,
                "errors": len(doc_obj.validation_errors),
                "warnings": len(doc_obj.validation_warnings)
            },
            "processing_history": [s.model_dump() for s in doc_obj.processing_history],
            "stats": doc_obj.get_stats()
        }, f, indent=2)
    
    print(f"\n--- Pipeline Summary ---")
    print(f"Blocks:     {len(doc_obj.blocks)}")
    print(f"Figures:    {len(doc_obj.figures)}")
    print(f"Tables:     {len(doc_obj.tables)}")
    print(f"Valid:      {doc_obj.is_valid}")
    print(f"Errors:     {len(doc_obj.validation_errors)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
