import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.models.pipeline_document import PipelineDocument, ReviewStatus
from app.models.block import Block
from app.models.equation import Equation
from app.pipeline.validation.validator import DocumentValidator
from app.pipeline.export.exporter import Exporter

def test_hitl_and_jats():
    print("Testing HITL and JATS Export...")
    
    # 1. Setup Document with low confidence and an equation
    doc = PipelineDocument(document_id="test_hitl_jats")
    doc.metadata.title = "High Energy Physics Analysis"
    doc.metadata.authors = ["John Doe", "Jane Smith"]
    doc.output_path = "storage/test_output.docx"
    
    # Block with low confidence
    b = Block(block_id="b1", text="Methodology Section")
    b.metadata["nlp_confidence"] = 0.65  # Below critical threshold
    doc.blocks = [b]
    
    # Equation with MathML
    eqn = Equation(
        equation_id="eqn_001",
        index=0,
        is_block=True,
        mathml='<math xmlns="http://www.w3.org/1998/Math/MathML"><msup><mrow><mtext>E</mtext></mrow><mrow><mtext>2</mtext></mrow></msup></math>'
    )
    doc.equations = [eqn]
    
    # 2. Verify HITL
    print("Running Validation (HITL)...")
    validator = DocumentValidator()
    validator.validate(doc)
    
    print(f"Review Status: {doc.review.status}")
    print(f"Flags: {doc.review.flags}")
    
    if doc.review.status == ReviewStatus.CRITICAL:
        print("VERIFICATION: HITL Critical Flag SUCCESS")
    else:
        print("VERIFICATION: HITL Flag FAILED")
        
    # 3. Verify JATS Export
    print("\nRunning JATS Export...")
    exporter = Exporter()
    xml_path = doc.output_path.replace(".docx", ".xml")
    exporter.export_jats(doc, xml_path)
    
    if os.path.exists(xml_path):
        with open(xml_path, "r", encoding="utf-8") as f:
            content = f.read()
            print("JATS XML Generated Successfully.")
            if "<disp-formula" in content and "<math" in content:
                print("VERIFICATION: JATS MathML SUCCESS")
            else:
                print("VERIFICATION: JATS MathML FAILED (tags missing)")
    else:
        print("VERIFICATION: JATS Export FAILED (file not found)")

if __name__ == "__main__":
    import traceback
    try:
        test_hitl_and_jats()
    except Exception as e:
        print(f"EXCEPTION type: {type(e)}")
        if hasattr(e, "errors"):
             print(f"VALIDATION ERRORS: {e.errors()}")
        print(f"EXCEPTION str: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
