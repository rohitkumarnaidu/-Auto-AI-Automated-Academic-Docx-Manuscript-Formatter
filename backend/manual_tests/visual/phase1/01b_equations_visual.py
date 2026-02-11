import os
import sys
from pathlib import Path

# Add backend to path (Depth 3: manual_tests/visual/phase1)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from app.pipeline.parsing.parser import DocxParser

def highlight_equations(input_path):
    print(f"\n🚀 PHASE 1: EQUATION DETECTION VISUAL")
    print(f"Target: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return

    # 1. Pipeline Execution
    parser = DocxParser()
    blocks = parser.parse_docx(input_path)
    
    # 2. Annotation
    doc = Document(input_path)
    # We look for blocks that are equations
    # For now, we mock the highlight logic based on keywords or OMML presence if we had easy access
    # In a real visual test, we'd iterate through paragraphs and check for oMath elements
    
    count = 0
    for para in doc.paragraphs:
        # Check for Math elements in XML
        if 'pos=\"' in para._p.xml or '<m:oMath' in para._p.xml:
            for run in para.runs:
                run.font.highlight_color = WD_COLOR_INDEX.TURQUOISE
            count += 1

    # 3. Save
    output_dir = Path("manual_tests/visual_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "01b_equations_annotated.docx"
    doc.save(output_file)
    
    print(f"\n--- Analysis Summary ---")
    print(f"Equations Highlighted: {count}")
    print(f"------------------------")
    print(f"\n✅ SUCCESS: Result saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 01b_equations_visual.py <docx_path>")
        sys.exit(1)
    highlight_equations(sys.argv[1])
