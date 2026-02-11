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
    blocks = classifier.classify_blocks(blocks)
    
    # 2. Annotate DOCX
    doc = Document(input_path)
    
    # Dashboard
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 1 (REFERENCES) ---")
    p.runs[0].bold = True
    ref_blocks = [b for b in blocks if b.type == BlockType.REFERENCES]
    doc.paragraphs[1].insert_paragraph_before(f"Reference blocks detected: {len(ref_blocks)}")
    doc.paragraphs[2].insert_paragraph_before("--------------------------------------------------\n")

    for block in ref_blocks:
        for para in doc.paragraphs:
            if block.text.strip() == para.text.strip():
                for run in para.runs:
                    run.font.highlight_color = WD_COLOR_INDEX.PINK
                break
                    
    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 04_references.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/04_references_annotated.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
