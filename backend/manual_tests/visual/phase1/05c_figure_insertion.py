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
from app.pipeline.figures.inserter import FigureInserter

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = CaptionMatcher()
    numberer = FigureNumbering()
    inserter = FigureInserter()
    
    blocks = parser.parse_docx(input_path)
    blocks = detector.detect_structure(blocks)
    blocks = classifier.classify_blocks(blocks)
    figures = matcher.match_captions(blocks)
    figures = numberer.number_figures(figures)
    figures_with_anchors = inserter.find_insertion_points(blocks, figures)
    
    # 2. Annotate DOCX
    doc = Document(input_path)
    
    # Dashboard
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 1 (FIGURE INSERTION) ---")
    p.runs[0].bold = True
    doc.paragraphs[1].insert_paragraph_before(f"Anchors identified: {len(figures_with_anchors)}")
    doc.paragraphs[2].insert_paragraph_before("--------------------------------------------------------\n")

    for fig in figures_with_anchors:
        anchor_idx = fig.metadata.get('anchor_index')
        if anchor_idx is not None:
            # We add a virtual indicator in the doc where the anchor is
            # (Note: blocks index matches doc paragraphs roughly in simple docs)
            # This is a bit complex in real docs, but for visual test we try to insert a placeholder
            try:
                anchor_para = doc.paragraphs[anchor_idx]
                p = anchor_para.insert_paragraph_before(f"[VIRTUAL FIGURE {fig.metadata.get('figure_number')} INSERTION POINT HERE]")
                p.runs[0].font.highlight_color = WD_COLOR_INDEX.GREEN
                p.runs[0].bold = True
            except:
                pass
                    
    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 05c_figure_insertion.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/05c_figure_insertion.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
