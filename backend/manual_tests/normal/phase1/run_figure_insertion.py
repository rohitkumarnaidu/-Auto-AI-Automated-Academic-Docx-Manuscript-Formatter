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

def main(input_path):
    print(f"\n🚀 PHASE 1: FIGURE INSERTION")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = CaptionMatcher()
    
    doc = parser.parse(input_path, "test_job")
    doc = normalizer.process(doc)
    doc = detector.process(doc)
    doc = classifier.process(doc)
    doc = matcher.process(doc)
    
    # Apply numbering and find insertion points
    figures = doc.figures
    blocks = doc.blocks
    
    for i, fig in enumerate(figures, 1):
        fig.number = i
        fig.metadata["figure_number"] = i
        
        # Find insertion point (after caption)
        if fig.caption_block_id:
            caption_block = next((b for b in blocks if b.block_id == fig.caption_block_id), None)
            if caption_block:
                fig.metadata["anchor_index"] = caption_block.index + 1
    
    # 2. Analysis
    anchors_found = len([f for f in figures if "anchor_index" in f.metadata])
    
    # 3. Save Output
    output_dir = Path("manual_tests/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "07_figure_insertion.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_figures": len(figures),
                "anchors_found": anchors_found
            },
            "figures": [
                {
                    "figure_id": f.figure_id,
                    "number": f.number,
                    "caption_block_id": f.caption_block_id,
                    "anchor_index": f.metadata.get("anchor_index")
                }
                for f in figures
            ]
        }, f, indent=2)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Total Figures: {len(figures)}")
    print(f"Anchors Found: {anchors_found}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_figure_insertion.py <docx_path>")
        sys.exit(1)
    main(sys.argv[1])
