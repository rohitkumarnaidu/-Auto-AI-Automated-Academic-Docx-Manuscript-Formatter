"""
Normal Test: Stage 2 Validation
Purpose: Verify document validation rules (errors/warnings) and save to JSON
Input: DOCX file
Output: manual_tests/outputs/12_validation.json
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
from app.pipeline.validation.validator import DocumentValidator

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_validation.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "12_validation.json"
    
    print("=" * 70)
    print("NORMAL TEST: STAGE 2 VALIDATION")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Running Pipeline stages...")
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    validator = DocumentValidator()
    
    doc_obj = parser.parse(input_path, "test_job_val")
    doc_obj = normalizer.process(doc_obj)
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    doc_obj = validator.process(doc_obj)
    
    # Analysis
    results = {
        "is_valid": doc_obj.is_valid,
        "errors": doc_obj.validation_errors,
        "warnings": doc_obj.validation_warnings,
        "stats": doc_obj.get_stats()
    }
    
    # Save Output
    print("[2/3] Saving validation results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n--- Results Summary ---")
    print(f"Valid:    {doc_obj.is_valid}")
    print(f"Errors:   {len(doc_obj.validation_errors)}")
    print(f"Warnings: {len(doc_obj.validation_warnings)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
