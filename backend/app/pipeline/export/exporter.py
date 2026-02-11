"""
Exporter Module - Handles saving of formatted documents.
"""

import os
from typing import Any, Optional
from app.models import PipelineDocument as Document
from app.pipeline.export.jats_generator import JATSGenerator

class Exporter:
    """
    Handles file output operations.
    """
    
    def process(self, document: Document) -> Document:
        """Standard pipeline stage entry point."""
        if hasattr(document, 'generated_doc') and document.generated_doc and document.output_path:
            self.export(document.generated_doc, document.output_path)
            
        # Optional: Generate JATS XML side-by-side if requested or as a production feature
        if document.output_path and document.output_path.endswith(".docx"):
            xml_path = document.output_path.replace(".docx", ".xml")
            self.export_jats(document, xml_path)
            
        return document

    def export(self, word_doc: Any, output_path: str) -> str:
        """Save the Word document to disk."""
        if not word_doc:
            return None
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        word_doc.save(output_path)
        return output_path

    def export_jats(self, doc_obj: Document, output_path: str) -> Optional[str]:
        """Generate and save JATS XML."""
        try:
            generator = JATSGenerator()
            xml_content = generator.to_xml(doc_obj)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            return output_path
        except Exception as e:
            print(f"Exporter: JATS export failed: {e}")
            return None
