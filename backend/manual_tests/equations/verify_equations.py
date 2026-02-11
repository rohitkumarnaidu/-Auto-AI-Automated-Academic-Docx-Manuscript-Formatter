import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.pipeline.equations.standardizer import get_equation_standardizer
from app.models import PipelineDocument, Equation

def test_equation_conversion():
    print("Testing EquationStandardizer...")
    
    # Sample OMML Fragment (a^2 + b^2 = c^2)
    omml = """
    <m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
      <m:r><m:t>a</m:t></m:r>
      <m:sSup>
        <m:e><m:r><m:t>a</m:t></m:r></m:e>
        <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
      </m:sSup>
      <m:r><m:t>+</m:t></m:r>
      <m:r><m:t>b</m:t></m:r>
      <m:sSup>
        <m:e><m:r><m:t>b</m:t></m:r></m:e>
        <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
      </m:sSup>
      <m:r><m:t>=</m:t></m:r>
      <m:sSup>
        <m:e><m:r><m:t>c</m:t></m:r></m:e>
        <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
      </m:sSup>
    </m:oMath>
    """
    
    doc = PipelineDocument(document_id="test_eqn")
    eqn = Equation(
        equation_id="eqn_001",
        index=0,
        omml=omml.strip()
    )
    doc.equations = [eqn]
    
    standardizer = get_equation_standardizer()
    standardizer.process(doc)
    
    print(f"Results for {eqn.equation_id}:")
    if eqn.mathml:
        print("MathML Generated Successfully:")
        print(eqn.mathml)
        if "<math" in eqn.mathml and "<msup" in eqn.mathml:
            print("VERIFICATION: SUCCESS (MathML contains math and msup tags)")
        else:
            print("VERIFICATION: PARTIAL (Tags missing)")
    else:
        print("VERIFICATION: FAILED (No MathML generated)")

if __name__ == "__main__":
    test_equation_conversion()
