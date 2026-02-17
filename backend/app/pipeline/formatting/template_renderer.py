"""
Template Renderer - Jinja2/docxtpl rendering for manuscript output.
"""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from docx import Document as WordDocument
from docxtpl import DocxTemplate

from app.models import Block, PipelineDocument as Document


class TemplateRenderer:
    """
    Renders pipeline documents into DOCX using Jinja2 tags in docxtpl templates.
    """

    def __init__(self, templates_dir: str = "app/templates"):
        self.templates_dir = Path(templates_dir)

    def render(self, document: Document, template_name: str = "ieee") -> DocxTemplate:
        """Render a template using document context."""
        template_path = self._resolve_template_path(template_name)
        context = self.build_context(document)

        tpl = DocxTemplate(str(template_path))
        tpl.render(context)
        return tpl

    def build_context(self, document: Document) -> Dict[str, Any]:
        """Build Jinja2 context from a pipeline document."""
        metadata = document.metadata
        abstract_text = (metadata.abstract or "").strip()
        if not abstract_text:
            abstract_text = self._first_block_text(document.blocks, "abstract_body")

        keywords = list(metadata.keywords or [])
        if not keywords:
            raw_keywords = self._first_block_text(document.blocks, "keywords_body")
            if raw_keywords:
                keywords = [item.strip() for item in raw_keywords.split(",") if item.strip()]

        authors = list(metadata.authors or [])
        if not authors:
            authors = self._all_block_text(document.blocks, "author")

        affiliations = list(metadata.affiliations or [])
        if not affiliations:
            affiliations = self._all_block_text(document.blocks, "affiliation")

        title = (metadata.title or "").strip()
        if not title:
            title = self._first_block_text(document.blocks, "title")
        if not title:
            title = document.original_filename or "Untitled Manuscript"

        references = self._collect_references(document)
        sections = self._collect_sections(document.blocks)

        formatting_options = document.formatting_options or {}

        return {
            "title": title,
            "authors": authors,
            "affiliations": affiliations,
            "date": datetime.utcnow().strftime("%B %d, %Y"),
            "abstract": abstract_text,
            "keywords": keywords,
            "sections": sections,
            "references": references,
            "cover_page": formatting_options.get("cover_page", True),
            "toc": formatting_options.get("toc", False),
            "page_numbers": formatting_options.get("page_numbers", True),
            "page_number": formatting_options.get("page_number", "1"),
        }

    def _resolve_template_path(self, template_name: str) -> Path:
        style = (template_name or "ieee").lower()
        candidate = self.templates_dir / style / "template.docx"
        if candidate.is_file():
            return candidate
        return self._build_fallback_template()

    def _build_fallback_template(self) -> Path:
        """Create a temporary fallback DOCX template if none exists."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            temp_path = Path(tmp.name)
        doc = WordDocument()
        doc.add_paragraph("{{ title }}", style="Title")
        doc.add_paragraph("{% for section in sections %}")
        doc.add_paragraph("{{ section.heading }}")
        doc.add_paragraph("{% for paragraph in section.paragraphs %}{{ paragraph }}{% endfor %}")
        doc.add_paragraph("{% endfor %}")
        doc.save(str(temp_path))
        return temp_path

    def _collect_references(self, document: Document) -> List[str]:
        if document.references:
            ordered = sorted(document.references, key=lambda ref: ref.index)
            refs = [
                (ref.formatted_text or ref.raw_text or "").strip()
                for ref in ordered
                if (ref.formatted_text or ref.raw_text or "").strip()
            ]
            if refs:
                return refs

        ref_blocks = [
            block.text.strip()
            for block in sorted(document.blocks, key=lambda b: b.index)
            if str(block.block_type).lower() == "reference_entry" and block.text.strip()
        ]
        return ref_blocks

    def _collect_sections(self, blocks: List[Block]) -> List[Dict[str, Any]]:
        """Group non-reference content into heading sections."""
        sections: List[Dict[str, Any]] = []
        current_heading = "Body"
        current_paragraphs: List[str] = []

        skip_types = {
            "title",
            "author",
            "affiliation",
            "abstract_heading",
            "abstract_body",
            "keywords_heading",
            "keywords_body",
            "references_heading",
            "reference_entry",
            "figure_caption",
            "table_caption",
        }

        for block in sorted(blocks, key=lambda b: b.index):
            block_type = str(block.block_type).lower()
            text = (block.text or "").strip()
            if not text or block_type in skip_types:
                continue

            if block_type.startswith("heading_"):
                if current_paragraphs:
                    sections.append({"heading": current_heading, "paragraphs": current_paragraphs})
                    current_paragraphs = []
                current_heading = text
                continue

            current_paragraphs.append(text)

        if current_paragraphs:
            sections.append({"heading": current_heading, "paragraphs": current_paragraphs})

        return sections

    def _first_block_text(self, blocks: List[Block], block_type: str) -> str:
        for block in sorted(blocks, key=lambda b: b.index):
            if str(block.block_type).lower() == block_type:
                value = (block.text or "").strip()
                if value:
                    return value
        return ""

    def _all_block_text(self, blocks: List[Block], block_type: str) -> List[str]:
        values: List[str] = []
        for block in sorted(blocks, key=lambda b: b.index):
            if str(block.block_type).lower() == block_type:
                value = (block.text or "").strip()
                if value:
                    values.append(value)
        return values
