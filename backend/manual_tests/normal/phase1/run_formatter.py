"""
Normal Test: Stage 3 Formatting
Purpose: Verify final formatted output generation and save result to JSON
Input: DOCX file
Output: manual_tests/outputs/formatted_result.json
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
from app.pipeline.validation import DocumentValidator
from app.pipeline.formatting.formatter import Formatter

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_formatter.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "formatted_result.json"
    
    print("=" * 70)
    print("NORMAL TEST: STAGE 3 FORMATTING")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Running Full Pipeline...")
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    fig_matcher = CaptionMatcher()
    tab_matcher = TableCaptionMatcher()
    ref_parser = ReferenceParser()
    validator = DocumentValidator()
    formatter = Formatter()
    
    doc_obj = parser.parse(input_path, "test_job_format")
    doc_obj = normalizer.process(doc_obj)
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    doc_obj = fig_matcher.process(doc_obj)
    doc_obj = tab_matcher.process(doc_obj)
    doc_obj = ref_parser.process(doc_obj)
    doc_obj = validator.process(doc_obj)
    doc_obj = formatter.process(doc_obj)
    
    # Analysis
    has_formatted = hasattr(doc_obj, 'generated_doc_path') and doc_obj.generated_doc_path is not None
    
    # Save Output
    print("[2/3] Saving formatting results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "formatting_successful": has_formatted,
                "template": doc_obj.metadata.get('template_name', 'None'),
                "total_blocks": len(doc_obj.blocks),
                "is_valid": doc_obj.is_valid
            },
            "processing_history": [s.model_dump() for s in doc_obj.processing_history],
            "formatted_doc_path": str(doc_obj.generated_doc_path) if has_formatted else None
        }, f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Formatting Successful: {has_formatted}")
    print(f"Template Applied:      {doc_obj.metadata.get('template_name', 'None')}")
    print(f"Valid:                 {doc_obj.is_valid}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
