import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.validation.validator import DocumentValidator

def main(input_path):
    print(f"\n🚀 PHASE 2: VALIDATION")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    validator = DocumentValidator()
    
    doc = parser.parse(input_path, "test_job")
    doc = normalizer.process(doc)
    doc = detector.process(doc)
    doc = classifier.process(doc)
    doc = validator.process(doc)
    
    # 2. Analysis
    validation_results = {
        "is_valid": doc.is_valid,
        "errors": doc.validation_errors,
        "warnings": doc.validation_warnings,
        "stats": doc.get_stats()
    }
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "12_validation.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Valid: {doc.is_valid}")
    print(f"Errors: {len(doc.validation_errors)}")
    print(f"Warnings: {len(doc.validation_warnings)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_validation.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
