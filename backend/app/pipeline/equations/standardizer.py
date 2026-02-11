import os
from typing import List
from lxml import etree
from app.models import PipelineDocument, Equation

class EquationStandardizer:
    """
    Pipeline stage to standardize mathematical equations.
    Converts OMML (Word) to MathML and LaTeX.
    """
    
    def __init__(self, xsl_path: str = None):
        if xsl_path is None:
            # Default to bundled XSL in the same directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            xsl_path = os.path.join(base_dir, "omml2mml.xsl")
            
        self.xsl_path = xsl_path
        self._xslt = None
        
        if os.path.exists(self.xsl_path):
            try:
                xslt_doc = etree.parse(self.xsl_path)
                self._xslt = etree.XSLT(xslt_doc)
            except Exception as e:
                print(f"EquationStandardizer: Failed to load XSLT: {e}")
        else:
            print(f"EquationStandardizer: XSLT not found at {self.xsl_path}")

    def process(self, doc_obj: PipelineDocument) -> PipelineDocument:
        """Standardize all equations in the document."""
        if not doc_obj.equations:
            return doc_obj
            
        success_count = 0
        failure_count = 0
        
        for eqn in doc_obj.equations:
            if eqn.omml:
                # 1. Convert to MathML
                mathml = self._convert_omml_to_mathml(eqn.omml)
                if mathml:
                    eqn.mathml = mathml
                    success_count += 1
                else:
                    failure_count += 1
                    
                # 2. Heuristic LaTeX extraction (Placeholder)
                # In a real production system, we'd use a more robust converter like pandoc
                # or a specifically trained model, but for now we preserve structural text.
                if not eqn.metadata:
                    eqn.metadata = {}
                eqn.metadata["conversion_engine"] = "xslt-1.0"
                
        # Log detailed conversion statistics
        total = success_count + failure_count
        message = f"Converted {success_count}/{total} equations to MathML"
        if failure_count > 0:
            message += f" ({failure_count} failed)"
            
        doc_obj.add_processing_stage(
            stage_name="equation_standardization",
            status="success" if failure_count == 0 else "partial",
            message=message
        )
        return doc_obj

    def _convert_omml_to_mathml(self, omml_xml: str) -> str:
        """Apply XSLT transformation to OMML string."""
        if not self._xslt:
            return ""
            
        try:
            # Parse OMML string
            dom = etree.fromstring(omml_xml)
            
            # Validate and normalize namespaces
            # Ensure OMML namespace is present
            omml_ns = "http://schemas.openxmlformats.org/officeDocument/2006/math"
            if dom.nsmap and None not in dom.nsmap:
                # If no default namespace, check if OMML namespace exists
                has_omml_ns = any(ns == omml_ns for ns in dom.nsmap.values())
                if not has_omml_ns:
                    print(f"EquationStandardizer: Warning - OMML namespace not found, attempting conversion anyway")
            
            # Apply XSLT transformation
            new_dom = self._xslt(dom)
            return etree.tostring(new_dom, encoding='unicode', pretty_print=True)
        except etree.XMLSyntaxError as e:
            print(f"EquationStandardizer: XML syntax error: {e}")
            return ""
        except Exception as e:
            print(f"EquationStandardizer: Conversion error: {e}")
            return ""

# Singleton Instance
_standardizer = None

def get_equation_standardizer() -> EquationStandardizer:
    global _standardizer
    if _standardizer is None:
        _standardizer = EquationStandardizer()
    return _standardizer
