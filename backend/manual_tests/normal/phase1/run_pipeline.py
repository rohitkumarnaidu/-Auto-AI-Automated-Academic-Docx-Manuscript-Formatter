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
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.pipeline.tables.caption_matcher import TableCaptionMatcher
from app.pipeline.references.parser import ReferenceParser
from app.pipeline.validation.validator import DocumentValidator

def main(input_path):
    print(f"\n🚀 FULL PIPELINE (END-TO-END)")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution (All Stages)
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    fig_matcher = CaptionMatcher()
    tab_matcher = TableCaptionMatcher()
    ref_parser = ReferenceParser()
    validator = DocumentValidator()
    
    doc = parser.parse(input_path, "test_job")
    doc = normalizer.process(doc)
    doc = detector.process(doc)
    doc = classifier.process(doc)
    doc = fig_matcher.process(doc)
    doc = tab_matcher.process(doc)
    doc = ref_parser.process(doc)
    doc = validator.process(doc)
    
    # 2. Analysis
    blocks = doc.blocks
    figures = doc.figures
    tables = doc.tables
    references = doc.references
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "pipeline_audit.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_blocks": len(blocks),
                "figures": len(figures),
                "tables": len(tables),
                "references": len(references),
                "is_valid": doc.is_valid,
                "errors": len(doc.validation_errors),
                "warnings": len(doc.validation_warnings)
            },
            "processing_history": [s.model_dump() for s in doc.processing_history],
            "stats": doc.get_stats()
        }, f, indent=2)
    
    print(f"\n--- Pipeline Summary ---")
    print(f"Blocks: {len(blocks)}")
    print(f"Figures: {len(figures)}")
    print(f"Tables: {len(tables)}")
    print(f"References: {len(references)}")
    print(f"Valid: {doc.is_valid}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
