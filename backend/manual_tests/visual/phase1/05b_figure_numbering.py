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
from app.pipeline.figures.caption_matcher import CaptionMatcher
from app.pipeline.figures.numbering import FigureNumbering

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
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
    
    # 2. Annotate DOCX
    doc = Document(input_path)
    
    # Dashboard
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 1 (FIGURE NUMBERING) ---")
    p.runs[0].bold = True
    doc.paragraphs[1].insert_paragraph_before(f"Figures numbered: {len(numbered_figures)}")
    doc.paragraphs[2].insert_paragraph_before("-------------------------------------------------------\n")

    for fig in numbered_figures:
        caption_text = fig.metadata.get('caption')
        if caption_text:
            for para in doc.paragraphs:
                if caption_text.strip() == para.text.strip():
                    for run in para.runs:
                        run.font.highlight_color = WD_COLOR_INDEX.RED
                    para.add_run(f" [FIGURE {fig.metadata.get('figure_number')}]").font.bold = True
                    break
                    
    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 05b_figure_numbering.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/05b_figure_numbering.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
