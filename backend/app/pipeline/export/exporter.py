"""
Exporter Module - Handles saving of formatted documents.
"""

import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.models import PipelineDocument as Document
from app.pipeline.export.jats_generator import JATSGenerator
from app.pipeline.export.pdf_exporter import PDFExporter

class Exporter:
    """
    Handles file output operations.

    Supports DOCX, PDF, JATS XML, JSON, and Markdown exports.
    """
    
    def __init__(self):
        self.pdf_exporter = PDFExporter()
    
    def process(self, document: Document) -> Document:
        """Standard pipeline stage entry point."""
        export_formats = self._get_export_formats(document)

        if "docx" in export_formats and hasattr(document, 'generated_doc') and document.generated_doc and document.output_path:
            self.export(document.generated_doc, document.output_path)

        if document.output_path and document.output_path.endswith(".docx"):
            if "json" in export_formats:
                json_path = document.output_path.replace(".docx", ".json")
                self.export_json(document, json_path)

            if "markdown" in export_formats:
                md_path = document.output_path.replace(".docx", ".md")
                self.export_markdown(document, md_path)

            if "pdf" in export_formats:
                try:
                    # PDF export requires the DOCX to be saved first
                    output_dir = os.path.dirname(document.output_path)
                    self.pdf_exporter.convert_to_pdf(document.output_path, output_dir)
                except Exception as e:
                    print(f"Exporter: PDF export failed: {e}")

            # Keep JATS side-by-side for compatibility with existing pipeline behavior.
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

    def export_json(self, doc_obj: Document, output_path: str) -> Optional[str]:
        """Export document with metadata to JSON."""
        try:
            payload = self._build_export_payload(doc_obj)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            return output_path
        except Exception as e:
            print(f"Exporter: JSON export failed: {e}")
            return None

    def export_markdown(self, doc_obj: Document, output_path: str) -> Optional[str]:
        """Export document with metadata and content to Markdown."""
        try:
            markdown = self._build_markdown(doc_obj)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            return output_path
        except Exception as e:
            print(f"Exporter: Markdown export failed: {e}")
            return None

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

    def _get_export_formats(self, document: Document) -> List[str]:
        """
        Resolve export formats from formatting options.
        Defaults to DOCX + JSON + Markdown.
        """
        options = document.formatting_options or {}
        raw_formats = options.get("export_formats", ["docx", "json", "markdown"])

        if not isinstance(raw_formats, list):
            raw_formats = [str(raw_formats)]

        normalized: List[str] = []
        for fmt in raw_formats:
            name = str(fmt).strip().lower()
            if name and name not in normalized:
                normalized.append(name)

        # DOCX remains primary output artifact.
        if "docx" not in normalized:
            normalized.insert(0, "docx")

        return normalized

    def _build_export_payload(self, doc_obj: Document) -> Dict[str, Any]:
        """Create a serializable export payload preserving metadata."""
        template_name = doc_obj.template.template_name if doc_obj.template else None

        return {
            "document_id": doc_obj.document_id,
            "original_filename": doc_obj.original_filename,
            "source_path": doc_obj.source_path,
            "output_path": doc_obj.output_path,
            "template": template_name,
            "metadata": doc_obj.metadata.model_dump(mode="json"),
            "stats": doc_obj.get_stats(),
            "validation": {
                "is_valid": doc_obj.is_valid,
                "errors": doc_obj.validation_errors,
                "warnings": doc_obj.validation_warnings,
            },
            "blocks": [block.model_dump(mode="json") for block in doc_obj.blocks],
            "references": [ref.model_dump(mode="json") for ref in doc_obj.references],
            "figures": [figure.model_dump(mode="json") for figure in doc_obj.figures],
            "tables": [table.model_dump(mode="json") for table in doc_obj.tables],
            "equations": [equation.model_dump(mode="json") for equation in doc_obj.equations],
            "processing_history": [stage.model_dump(mode="json") for stage in doc_obj.processing_history],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    def _build_markdown(self, doc_obj: Document) -> str:
        """Build markdown export preserving metadata and content."""
        metadata = doc_obj.metadata
        lines: List[str] = []

        title = metadata.title or doc_obj.original_filename or "Untitled Manuscript"
        lines.append(f"# {title}")
        lines.append("")

        if metadata.authors:
            lines.append(f"**Authors:** {', '.join(metadata.authors)}")
        if metadata.affiliations:
            lines.append(f"**Affiliations:** {'; '.join(metadata.affiliations)}")
        if metadata.doi:
            lines.append(f"**DOI:** {metadata.doi}")
        if doc_obj.template and doc_obj.template.template_name:
            lines.append(f"**Template:** {doc_obj.template.template_name}")
        lines.append("")

        if metadata.abstract:
            lines.append("## Abstract")
            lines.append(metadata.abstract)
            lines.append("")

        if metadata.keywords:
            lines.append(f"**Keywords:** {', '.join(metadata.keywords)}")
            lines.append("")

        current_heading: Optional[str] = None
        for block in sorted(doc_obj.blocks, key=lambda b: b.index):
            block_type = str(block.block_type).lower()
            text = (block.text or "").strip()
            if not text:
                continue

            if block_type.startswith("heading_"):
                current_heading = text
                lines.append(f"## {current_heading}")
                lines.append("")
                continue

            if block_type in {"reference_entry", "references_heading"}:
                continue

            lines.append(text)
            lines.append("")

        references = [
            (ref.formatted_text or ref.raw_text or "").strip()
            for ref in sorted(doc_obj.references, key=lambda r: r.index)
            if (ref.formatted_text or ref.raw_text or "").strip()
        ]
        if references:
            lines.append("## References")
            lines.append("")
            for idx, ref_text in enumerate(references, start=1):
                lines.append(f"{idx}. {ref_text}")
            lines.append("")

        return "\n".join(lines).strip() + "\n"
