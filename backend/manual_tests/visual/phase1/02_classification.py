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
from app.models.block import BlockType

def annotate_visual(input_path, output_path):
    print(f"Annotating {input_path}")
    
    # 1. Pipeline Execution: Parse -> Normalize -> Structure -> Classify
    parser = DocxParser()
    normalizer = Normalizer()
    detector = StructureDetector()
    classifier = ContentClassifier()
    
    doc = parser.parse(input_path, "visual_test")
    doc = normalizer.process(doc)
    doc = detector.process(doc)
    doc = classifier.process(doc)
    
    blocks = doc.blocks
    
    # 2. Annotate DOCX
    annotated_doc = Document(input_path)
    
    # Color mapping for BlockTypes
    color_map = {
        BlockType.TITLE: WD_COLOR_INDEX.PINK,
        BlockType.AUTHOR: WD_COLOR_INDEX.BLUE,
        BlockType.AFFILIATION: WD_COLOR_INDEX.TEAL,
        BlockType.ABSTRACT_HEADING: WD_COLOR_INDEX.BRIGHT_GREEN,
        BlockType.ABSTRACT_BODY: WD_COLOR_INDEX.GREEN,
        BlockType.HEADING_1: WD_COLOR_INDEX.YELLOW,
        BlockType.HEADING_2: WD_COLOR_INDEX.YELLOW,
        BlockType.HEADING_3: WD_COLOR_INDEX.YELLOW,
        BlockType.HEADING_4: WD_COLOR_INDEX.YELLOW,
        BlockType.REFERENCES_HEADING: WD_COLOR_INDEX.YELLOW,
        BlockType.REFERENCE_ENTRY: WD_COLOR_INDEX.GRAY_25,
        BlockType.FIGURE_CAPTION: WD_COLOR_INDEX.TURQUOISE,
        BlockType.TABLE_CAPTION: WD_COLOR_INDEX.TURQUOISE,
    }
    
    # Dashboard insertion
    if annotated_doc.paragraphs:
        first_para = annotated_doc.paragraphs[0]
        
        # Count by type
        type_counts = {}
        for b in blocks:
            bt = b.block_type
            type_counts[bt] = type_counts.get(bt, 0) + 1
        
        first_para.insert_paragraph_before("------------------------------------------------\n")
        for bt, count in sorted(type_counts.items(), key=lambda x: str(x[0])):
            first_para.insert_paragraph_before(f"{bt.value}: {count}")
        first_para.insert_paragraph_before(f"Total Blocks: {len(blocks)}")
        
        header_p = first_para.insert_paragraph_before(
            "--- QA VISUAL DASHBOARD: PHASE 1 (CLASSIFICATION) ---"
        )
        if header_p.runs:
            header_p.runs[0].bold = True
    
    # Highlight blocks by type
    for block in blocks:
        idx = block.index
        if 0 <= idx < len(annotated_doc.paragraphs):
            para = annotated_doc.paragraphs[idx]
            
            # Apply color if mapped
            if block.block_type in color_map:
                for run in para.runs:
                    run.font.highlight_color = color_map[block.block_type]
                
                # Add type annotation
                para.add_run(f" [TYPE: {block.block_type.value.upper()}]").font.bold = True
                    
    annotated_doc.save(output_path)
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
