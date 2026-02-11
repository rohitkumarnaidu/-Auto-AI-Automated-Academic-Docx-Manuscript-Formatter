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
from app.pipeline.tables.caption_matcher import TableCaptionMatcher
from app.models import BlockType

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    parser = DocxParser()
    detector = StructureDetector()
    classifier = ContentClassifier()
    fig_matcher = CaptionMatcher()
    tab_matcher = TableCaptionMatcher()
    
    blocks = parser.parse_docx(input_path)
    blocks = detector.detect_structure(blocks)
    blocks = classifier.classify_blocks(blocks)
    
    # Process Figures
    figures = fig_matcher.match_captions(blocks)
    
    # Process Tables
    raw_tables = [b for b in blocks if b.type == BlockType.TABLE]
    tables = tab_matcher.match_captions(blocks, raw_tables)
    
    # 2. Annotate DOCX
    doc = Document(input_path)
    
    # Dashboard
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 1 (FIGURES & TABLES) ---")
    p.runs[0].bold = True
    doc.paragraphs[1].insert_paragraph_before(f"Figures matched: {sum(1 for f in figures if f.metadata.get('caption'))}")
    doc.paragraphs[2].insert_paragraph_before(f"Tables matched:  {sum(1 for t in tables if t.metadata.get('caption'))}")
    doc.paragraphs[3].insert_paragraph_before("------------------------------------------------------\n")

    # Annotate captions
    for block in blocks:
        color = None
        if block.type == BlockType.FIGURE_CAPTION: color = WD_COLOR_INDEX.RED
        if block.type == BlockType.TABLE_CAPTION: color = WD_COLOR_INDEX.BLUE
        
        if color:
            for para in doc.paragraphs:
                if block.text.strip() == para.text.strip():
                    for run in para.runs:
                        run.font.highlight_color = color
                    para.add_run(f" [MATCHED]").font.bold = True
                    break

    # Add extraction preview at the end
    doc.add_page_break()
    doc.add_heading("Extraction Preview (Data Matrices)", level=1)
    
    for i, table in enumerate(tables):
        doc.add_heading(f"Table {i+1}: {table.metadata.get('caption', 'Unlabeled')}", level=2)
        if hasattr(table, 'data') and table.data:
            rows = len(table.data)
            cols = len(table.data[0]) if rows > 0 else 0
            if rows > 0 and cols > 0:
                t = doc.add_table(rows=rows, cols=cols)
                t.style = 'Table Grid'
                for r_idx, row_data in enumerate(table.data):
                    for c_idx, cell_text in enumerate(row_data):
                        t.cell(r_idx, c_idx).text = str(cell_text)

    doc.save(output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 03_figures_tables.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/03_figures_tables_annotated.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
