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
from app.pipeline.classification.classifier import ContentClassifier
from app.pipeline.tables.caption_matcher import TableCaptionMatcher
from app.models.block import BlockType

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    matcher = TableCaptionMatcher()
    
    doc = parser.parse(input_path, "visual_test")
    doc = normalizer.process(doc)
    doc = detector.process(doc)
    doc = classifier.process(doc)
    doc = matcher.process(doc)
    
    blocks = doc.blocks
    tables = doc.tables
    
    # Apply numbering
    for i, tab in enumerate(tables, 1):
        tab.number = i
        tab.metadata["table_number"] = i
    
    # 2. Annotate DOCX
    annotated_doc = Document(input_path)
    
    # Dashboard insertion
    if annotated_doc.paragraphs:
        first_para = annotated_doc.paragraphs[0]
        
        first_para.insert_paragraph_before("------------------------------------------------\n")
        first_para.insert_paragraph_before(f"Tables Numbered: {len(tables)}")
        first_para.insert_paragraph_before(f"Total Blocks: {len(blocks)}")
        
        header_p = first_para.insert_paragraph_before(
            "--- QA VISUAL DASHBOARD: PHASE 1 (TABLE NUMBERING) ---"
        )
        if header_p.runs:
            header_p.runs[0].bold = True
    
    # Highlight table captions with numbers
    for tab in tables:
        if tab.caption_block_id:
            caption_block = next((b for b in blocks if b.block_id == tab.caption_block_id), None)
            if caption_block:
                idx = caption_block.index
                if 0 <= idx < len(annotated_doc.paragraphs):
                    para = annotated_doc.paragraphs[idx]
                    for run in para.runs:
                        run.font.highlight_color = WD_COLOR_INDEX.TURQUOISE
                    para.add_run(f" [TABLE {tab.number}]").font.bold = True
                    
    annotated_doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 06b_table_numbering.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/06b_table_numbering_annotated.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
