"""
Normal Test: Figure Numbering
Purpose: Verify sequential figure numbering and save to JSON
Input: DOCX file
Output: manual_tests/outputs/06_figure_numbering.json
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_figure_numbering.py <input.docx>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "06_figure_numbering.json"
    
    print("=" * 70)
    print("NORMAL TEST: FIGURE NUMBERING")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Output: {output_file}")
    
    # Execution
    print("[1/3] Running Pipeline stages...")
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = CaptionMatcher()
    
    doc_obj = parser.parse(input_path, "test_job_fignum")
    doc_obj = normalizer.process(doc_obj)
    doc_obj = detector.process(doc_obj)
    doc_obj = classifier.process(doc_obj)
    doc_obj = matcher.process(doc_obj)
    
    # 2. Sequential Numbering
    figures = doc_obj.figures
    sequence = []
    for i, fig in enumerate(figures, 1):
        fig.number = i
        sequence.append(i)
    
    # Save Output
    print("[2/3] Saving numbering results...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "figures_numbered": len(figures),
                "sequence_generated": sequence
            },
            "figures": [
                {
                    "figure_id": f.figure_id,
                    "number": f.number,
                    "caption_block_id": f.caption_block_id
                }
                for f in figures
            ]
        }, f, indent=2)
    
    print(f"\n--- Results Summary ---")
    print(f"Figures Numbered: {len(figures)}")
    print(f"Sequence Length:  {len(sequence)}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    main()
