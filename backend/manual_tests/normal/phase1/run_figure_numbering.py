import os
import sys
import json
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/normal/phase1_identification)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.pipeline.figures.numbering import FigureNumbering

def main(input_path):
    print(f"\n🚀 PHASE 1: FIGURE NUMBERING")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = CaptionMatcher()
    numberer = FigureNumbering()
    
    blocks = parser.parse_docx(input_path)
    blocks = detector.detect_structure(blocks)
    blocks = classifier.classify_blocks(blocks)
    figures = matcher.match_captions(blocks)
    numbered_figures = numberer.number_figures(figures)
    
    # 2. Analysis
    numbers = [f.metadata.get('figure_number') for f in numbered_figures if f.metadata.get('figure_number')]
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "06_figure_numbering.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "figures_numbered": len(numbered_figures),
                "sequence": numbers
            },
            "figures": [b.model_dump() for b in numbered_figures]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Figures Numbered: {len(numbered_figures)}")
    print(f"Sequence: {numbers}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_figure_numbering.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
