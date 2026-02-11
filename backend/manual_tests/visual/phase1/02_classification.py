import os
import sys
from pathlib import Path
from docx import Document
from docx.enum.text import WD_COLOR_INDEX

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.classification.classifier import ContentClassifier
from app.models import BlockType

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    classifier = ContentClassifier()
    
    blocks = parser.parse_docx(input_path)
    blocks = detector.detect_structure(blocks)
    classified_blocks = classifier.classify_blocks(blocks)
    
    # 2. Annotate DOCX
    doc = Document(input_path)
    
    # Add Summary Dashboard at top
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 1 (CLASSIFICATION) ---")
    p.runs[0].bold = True
    
    counts = {}
    for b in classified_blocks:
        counts[b.type] = counts.get(b.type, 0) + 1
        
    for i, (btype, count) in enumerate(counts.items()):
        doc.paragraphs[i+1].insert_paragraph_before(f"{btype}: {count}")
    
    # Highlights mapping
    color_map = {
        BlockType.HEADING: WD_COLOR_INDEX.YELLOW,
        BlockType.FIGURE_CAPTION: WD_COLOR_INDEX.RED,
        BlockType.TABLE_CAPTION: WD_COLOR_INDEX.BLUE,
        BlockType.AFFILIATION: WD_COLOR_INDEX.GRAY_25,
        BlockType.AUTHOR: WD_COLOR_INDEX.BRIGHT_GREEN,
        BlockType.ABSTRACT: WD_COLOR_INDEX.TURQUOISE,
        BlockType.REFERENCES: WD_COLOR_INDEX.PINK
    }

    for block in classified_blocks:
        if block.type in color_map:
            for para in doc.paragraphs:
                if block.text.strip() == para.text.strip():
                    for run in para.runs:
                        run.font.highlight_color = color_map[block.type]
                    break
                    
    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 02_classification.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/02_classified_annotated.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
