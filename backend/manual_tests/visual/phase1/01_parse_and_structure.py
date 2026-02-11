import os
import sys
from pathlib import Path
from docx import Document
from docx.enum.text import WD_COLOR_INDEX

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.normalization.normalizer import Normalizer
from app.pipeline.structure_detection.detector import StructureDetector


def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    
    parsed_doc = parser.parse(input_path, "visual_test")
    normalized_doc = normalizer.process(parsed_doc)
    structured_doc = detector.process(normalized_doc)
    
    structured_blocks = structured_doc.blocks
    
    # 2. Annotate DOCX
    annotated_doc = Document(input_path)
    
    # Detect headings using metadata
    heading_blocks = [
        b for b in structured_blocks
        if b.metadata.get("is_heading_candidate", False)
    ]
    
    # Safe dashboard insertion
    if annotated_doc.paragraphs:
        first_para = annotated_doc.paragraphs[0]
        
        first_para.insert_paragraph_before("------------------------------------------------\n")
        first_para.insert_paragraph_before(f"Headings: {len(heading_blocks)}")
        first_para.insert_paragraph_before(f"Total Blocks: {len(structured_blocks)}")
        
        header_p = first_para.insert_paragraph_before(
            "--- QA VISUAL DASHBOARD: PHASE 1 (STRUCTURE) ---"
        )
        if header_p.runs:
            header_p.runs[0].bold = True

    # Highlight headings
    for block in heading_blocks:
        idx = block.index
        if 0 <= idx < len(annotated_doc.paragraphs):
            para = annotated_doc.paragraphs[idx]
            for run in para.runs:
                run.font.highlight_color = WD_COLOR_INDEX.YELLOW
            
            level = block.metadata.get("level", "?")
            para.add_run(f" [HEADING L{level}]").font.bold = True
                    
    annotated_doc.save(output_path)
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
