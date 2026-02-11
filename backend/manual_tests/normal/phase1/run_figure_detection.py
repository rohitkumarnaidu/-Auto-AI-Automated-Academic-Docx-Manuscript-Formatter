"""
Normal Test: Figure Detection
Purpose: Verify figure asset extraction and save to JSON
Input: DOCX file
Output: manual_tests/outputs/04_figures.json
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_figure_detection.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "04_figures.json"
    
    print("=" * 70)
    print("NORMAL TEST: FIGURE DETECTION")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Running Pipeline stages...")
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    
    doc_obj = parser.parse(input_path, "test_job_figdet")
    doc_obj = normalizer.process(doc_obj)
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    
    # Analysis
    figures = doc_obj.figures
    
    # Save Output
    print("[2/3] Saving figure results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "figures_detected": len(figures)
            },
            "figures": [fig.model_dump(exclude={"image_data"}) for fig in figures]
        }, f, indent=2, default=str)
    
    print(f"\n--- Results Summary ---")
    print(f"Figures Detected: {len(figures)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
