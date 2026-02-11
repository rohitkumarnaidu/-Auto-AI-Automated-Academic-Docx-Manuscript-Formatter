import os
import sys
from pathlib import Path
from docx import Document as WordDoc
from docx.enum.text import WD_COLOR_INDEX

# Add backend to path
# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# Fallback if running from backend root
if os.path.abspath(".").endswith("backend") and os.path.abspath(".") not in sys.path:
    sys.path.insert(0, os.path.abspath("."))

from app.pipeline.orchestrator import DocumentProcessor
from app.models import BlockType

def annotate_visual_full(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution
    processor = DocumentProcessor()
    result = processor.run_identification_only(input_path)
    
    # 2. Annotate DOCX
    doc = WordDoc(input_path)
    
    # Dashboard
    p = doc.paragraphs[0].insert_paragraph_before("--- QA VISUAL DASHBOARD: PHASE 2 (FULL ASSEMBLY) ---")
    p.runs[0].bold = True
    doc.paragraphs[1].insert_paragraph_before(f"Total Model Blocks: {len(result.blocks)}")
    doc.paragraphs[2].insert_paragraph_before(f"Review Flags: {len(result.metadata.review_flags if hasattr(result.metadata, 'review_flags') else [])}")
    doc.paragraphs[3].insert_paragraph_before("----------------------------------------------------\n")

    # Highlights mapping
    color_map = {
        BlockType.HEADING: WD_COLOR_INDEX.YELLOW,
        BlockType.FIGURE_CAPTION: WD_COLOR_INDEX.RED,
        BlockType.TABLE_CAPTION: WD_COLOR_INDEX.BLUE,
        BlockType.AUTHOR: WD_COLOR_INDEX.BRIGHT_GREEN,
    }

    for block in result.blocks:
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
        print("Usage: python 05_full_pipeline.py <docx_path>")
        sys.exit(1)
        
    input_docx = sys.argv[1]
    output_docx = "manual_tests/visual_outputs/05_full_pipeline_annotated.docx"
    
    os.makedirs("manual_tests/visual_outputs", exist_ok=True)
    annotate_visual_full(input_docx, output_docx)
    print(f"Done. Visual test saved to {output_docx}")
