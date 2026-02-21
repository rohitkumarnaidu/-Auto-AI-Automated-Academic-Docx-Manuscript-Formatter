"""
Exporter Module - Handles saving of formatted documents.
"""

import os
import json
import html as html_mod
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.models import PipelineDocument as Document
from app.pipeline.export.jats_generator import JATSGenerator
from app.pipeline.export.pdf_exporter import PDFExporter

logger = logging.getLogger(__name__)

class Exporter:
    """
    Handles file output operations.

    Supports DOCX, PDF, JATS XML, JSON, Markdown, HTML, and LaTeX exports.
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
                    logger.warning("Exporter: PDF export failed: %s", e)

            if "html" in export_formats:
                html_path = document.output_path.replace(".docx", ".html")
                self.export_html(document, html_path)

            if "latex" in export_formats:
                tex_path = document.output_path.replace(".docx", ".tex")
                self.export_latex(document, tex_path)

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
            logger.warning("Exporter: JSON export failed: %s", e)
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
            logger.warning("Exporter: Markdown export failed: %s", e)
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
            logger.warning("Exporter: JATS export failed: %s", e)
            return None

    def export_html(self, doc_obj: Document, output_path: str) -> Optional[str]:
        """Export document to HTML format."""
        try:
            markdown = self._build_markdown(doc_obj)
            lines = markdown.split('\n')
            html_lines = ["<!DOCTYPE html>", "<html>", "<head>", f"<title>{html_mod.escape(doc_obj.metadata.title or 'Document')}</title>", "</head>", "<body>"]
            
            in_list = False
            for line in lines:
                if not line.strip():
                    continue
                if line.startswith("# "):
                    html_lines.append(f"<h1>{html_mod.escape(line[2:])}</h1>")
                elif line.startswith("## "):
                    html_lines.append(f"<h2>{html_mod.escape(line[3:])}</h2>")
                elif line.startswith("**") and ":" in line:
                    parts = line[2:].split('**')
                    if len(parts) >= 2:
                        html_lines.append(f"<p><strong>{html_mod.escape(parts[0])}</strong>{html_mod.escape(parts[1])}</p>")
                elif line[0].isdigit() and len(line) > 1 and line[1] == ".":
                    if not in_list:
                        html_lines.append("<ol>")
                        in_list = True
                    html_lines.append(f"<li>{html_mod.escape(line[line.find('.')+1:].strip())}</li>")
                else:
                    if in_list:
                        html_lines.append("</ol>")
                        in_list = False
                    html_lines.append(f"<p>{html_mod.escape(line)}</p>")
            
            if in_list:
                html_lines.append("</ol>")
                
            html_lines.extend(["</body>", "</html>"])
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(html_lines))
            return output_path
        except Exception as e:
            logger.warning("Exporter: HTML export failed: %s", e)
            return None

    def export_latex(self, doc_obj: Document, output_path: str) -> Optional[str]:
        """Export document to LaTeX format."""
        try:
            tex_lines = [
                "\\documentclass{article}",
                "\\usepackage[utf8]{inputenc}",
                "\\usepackage{hyperref}",
                ""
            ]
            
            title = doc_obj.metadata.title or "Untitled Manuscript"
            tex_lines.append(f"\\title{{{title}}}")
            
            if doc_obj.metadata.authors:
                tex_lines.append(f"\\author{{{', '.join(doc_obj.metadata.authors)}}}")
                
            tex_lines.extend(["\\begin{document}", "\\maketitle", ""])
            
            if doc_obj.metadata.abstract:
                tex_lines.extend(["\\begin{abstract}", doc_obj.metadata.abstract, "\\end{abstract}", ""])
            
            for block in sorted(doc_obj.blocks, key=lambda b: b.index):
                block_type = str(block.block_type).lower()
                text = (block.text or "").strip()
                if not text:
                    continue
                    
                if block_type.startswith("heading_"):
                    if block.metadata.get("heading_level", 2) == 1:
                        tex_lines.append(f"\\section{{{text}}}")
                    else:
                        tex_lines.append(f"\\subsection{{{text}}}")
                elif block_type not in {"reference_entry", "references_heading"}:
                    escaped_text = text.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("#", "\\#").replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")
                    tex_lines.append(escaped_text + "\n")
                    
            references = [
                (ref.formatted_text or ref.raw_text or "").strip()
                for ref in sorted(doc_obj.references, key=lambda r: r.index)
                if (ref.formatted_text or ref.raw_text or "").strip()
            ]
            
            if references:
                tex_lines.extend(["\\begin{thebibliography}{99}"])
                for i, ref in enumerate(references):
                    escaped_ref = ref.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("#", "\\#").replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")
                    tex_lines.append(f"\\bibitem{{ref{i}}} {escaped_ref}")
                tex_lines.append("\\end{thebibliography}")
                
            tex_lines.append("\\end{document}")
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(tex_lines))
            return output_path
        except Exception as e:
            logger.warning("Exporter: LaTeX export failed: %s", e)
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
