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
from app.pipeline.tables.inserter import TableInserter
from app.models import BlockType

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    classifier = ContentClassifier()
    inserter = TableInserter()
    
    blocks = parser.parse_docx(input_path)
    blocks = detector.detect_structure(blocks)
    blocks = classifier.classify_blocks(blocks)
    tables = [b for b in blocks if b.type == BlockType.TABLE]
    tables_with_anchors = inserter.find_insertion_points(blocks, tables)
    
    # 2. Annotate DOCX
    doc = Document(input_path)
    
    # Dashboard
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 1 (TABLE INSERTION) ---")
    p.runs[0].bold = True
    doc.paragraphs[1].insert_paragraph_before(f"Anchors identified: {len(tables_with_anchors)}")
    doc.paragraphs[2].insert_paragraph_before("-------------------------------------------------------\n")

    for tab in tables_with_anchors:
        anchor_idx = tab.metadata.get('anchor_index')
        if anchor_idx is not None:
            try:
                anchor_para = doc.paragraphs[anchor_idx]
                p = anchor_para.insert_paragraph_before(f"[VIRTUAL TABLE INSERTION POINT HERE]")
                p.runs[0].font.highlight_color = WD_COLOR_INDEX.TURQUOISE
                p.runs[0].bold = True
            except:
                pass
                    
    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 06c_table_insertion.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/06c_table_insertion.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
