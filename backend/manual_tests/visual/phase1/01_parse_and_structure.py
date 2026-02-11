import os
import sys
from pathlib import Path
from docx import Document
from docx.enum.text import WD_COLOR_INDEX

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.structure_detection.detector import StructureDetector
from app.models import BlockType

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    
    blocks = parser.parse_docx(input_path)
    # Filter only blocks that the detector adds structure to
    structured_blocks = detector.detect_structure(blocks)
    
    # 2. Annotate DOCX
    doc = Document(input_path)
    
    # Add Summary Dashboard at top
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 1 (STRUCTURE) ---")
    p.runs[0].bold = True
    doc.paragraphs[1].insert_paragraph_before(f"Total Blocks: {len(structured_blocks)}")
    doc.paragraphs[2].insert_paragraph_before(f"Headings: {sum(1 for b in structured_blocks if b.type == BlockType.HEADING)}")
    doc.paragraphs[3].insert_paragraph_before("------------------------------------------------\n")

    # Match blocks to paragraphs and highlight
    # (Simple mapping for visual inspection)
    heading_count = 0
    for block in structured_blocks:
        if block.type == BlockType.HEADING:
            # Try to find the matching paragraph by text content
            for para in doc.paragraphs:
                if block.text.strip() == para.text.strip():
                    for run in para.runs:
                        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
                    # Add comment-like text
                    para.add_run(f" [HEADING L{block.metadata.get('level', '?')}]").font.bold = True
                    heading_count += 1
                    break
                    
    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 01_parse_and_structure.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/01_structure_annotated.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
