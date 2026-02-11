"""
Visual Test - Stage 2: Semantic Classification

Purpose: Verify semantic classification visually
Input: DOCX file
Output: Annotated DOCX with section labels

Usage:
    python manual_tests/visual/02_classification.py uploads/input.docx

Output:
    manual_tests/visual_outputs/02_classified_annotated.docx

Visual Inspection:
    - Open output DOCX in Microsoft Word
    - Blue annotations = Section labels (Abstract, Introduction, etc.)
    - Green highlights = High confidence classifications
    - Orange highlights = Low confidence (needs review)
"""

import sys
import os
from pathlib import Path
from docx import Document
from docx.shared import RGBColor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.pipeline.parsing.parser import DocxParser
from app.pipeline.structure_detection.detector import StructureDetector
from app.pipeline.intelligence.semantic_parser import SemanticParser

def add_annotation(paragraph, text, color_rgb):
    """Add colored annotation to paragraph."""
    run = paragraph.add_run(f" [{text}]")
    run.font.color.rgb = RGBColor(*color_rgb)
    run.font.bold = True

def main():
    if len(sys.argv) < 2:
        print("Usage: python 02_classification.py <input.docx>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = Path(__file__).parent.parent / "visual_outputs"
    output_path = output_dir / "02_classified_annotated.docx"
    
    print("=" * 70)
    print("VISUAL TEST - STAGE 2: SEMANTIC CLASSIFICATION")
    print("=" * 70)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()
    
    # Run pipeline stages 1-2
    print("[1/4] Parsing DOCX...")
    parser = DocxParser()
    doc_obj = parser.parse(input_path, document_id="visual_test_stage2")
    
    print("[2/4] Detecting structure...")
    detector = StructureDetector()
    doc_obj = detector.process(doc_obj)
    
    print("[3/4] Running semantic classification...")
    semantic_parser = SemanticParser()
    doc_obj.blocks = semantic_parser.detect_boundaries(doc_obj.blocks)
    
    # Count classifications
    sections = {}
    for block in doc_obj.blocks:
        intent = block.metadata.get('semantic_intent', 'UNKNOWN')
        sections[intent] = sections.get(intent, 0) + 1
    
    print(f"      ✓ Classified into {len(sections)} section types")
    
    # Create annotated DOCX
    print("[4/4] Creating annotated DOCX...")
    annotated_doc = Document(input_path)
    
    para_index = 0
    for block in doc_obj.blocks:
        if para_index >= len(annotated_doc.paragraphs):
            break
        
        para = annotated_doc.paragraphs[para_index]
        
        intent = block.metadata.get('semantic_intent', 'UNKNOWN')
        confidence = block.metadata.get('nlp_confidence', 0.0)
        
        # Color code by confidence
        if confidence >= 0.85:
            color = (0, 128, 0)  # Green - high confidence
        elif confidence >= 0.70:
            color = (0, 0, 255)  # Blue - medium confidence
        else:
            color = (255, 140, 0)  # Orange - low confidence
        
        add_annotation(para, f"{intent} ({confidence:.2f})", color)
        
        para_index += 1
    
    # Add summary
    summary = (
        f"=== CLASSIFICATION SUMMARY ===\n"
        f"Total Blocks: {len(doc_obj.blocks)}\n"
    )
    for section, count in sorted(sections.items()):
        summary += f"{section}: {count}\n"
    summary += "==============================\n"
    
    summary_para = annotated_doc.paragraphs[0].insert_paragraph_before(summary)
    summary_para.runs[0].font.color.rgb = RGBColor(0, 128, 0)
    summary_para.runs[0].bold = True
    
    annotated_doc.save(str(output_path))
    
    print()
    print("=" * 70)
    print("✅ STAGE 2 COMPLETE")
    print("=" * 70)
    print(f"Output saved to: {output_path}")
    print()
    print("NEXT STEP:")
    print("1. Open the output DOCX in Microsoft Word")
    print("2. Look for:")
    print("   - Green annotations = High confidence sections")
    print("   - Blue annotations = Medium confidence")
    print("   - Orange annotations = Low confidence (review needed)")
    print("3. Verify section labels are correct")
    print("4. Report any misclassifications before proceeding to Stage 3")
    print()

if __name__ == "__main__":
    main()
