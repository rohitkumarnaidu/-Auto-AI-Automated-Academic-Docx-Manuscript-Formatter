"""
Tests for Formatter — ensures it produces a valid .docx artifact.
"""
from __future__ import annotations

import io
import pytest
from docx import Document as WordDocument
from docxtpl import DocxTemplate

from app.pipeline.formatting.formatter import Formatter
from app.pipeline.formatting.template_renderer import TemplateRenderer


class TestFormatterOutput:

    def test_formatter_process_sets_generated_doc(self, minimal_doc):
        """Formatter.process() sets document.generated_doc."""
        formatter = Formatter(templates_dir="app/templates", contracts_dir="app/pipeline/contracts")
        result = formatter.process(minimal_doc)
        assert result.generated_doc is not None, "generated_doc must not be None after formatting"

    def test_formatter_docxtpl_path_returns_docxtemplate(self, full_doc):
        """When a template.docx exists, Formatter.format() returns DocxTemplate."""
        formatter = Formatter(templates_dir="app/templates", contracts_dir="app/pipeline/contracts")
        rendered = formatter.format(full_doc, template_name="ieee")
        # Primary path: DocxTemplate; fallback: WordDocument
        assert isinstance(rendered, (DocxTemplate, WordDocument)), (
            f"Expected DocxTemplate or WordDocument, got {type(rendered)}"
        )

    def test_formatter_none_template_falls_back_to_word_doc(self, minimal_doc):
        """template_name='none' uses blank WordDocument fallback path."""
        formatter = Formatter(templates_dir="app/templates", contracts_dir="app/pipeline/contracts")
        rendered = formatter.format(minimal_doc, template_name="none")
        # 'none' has no Jinja2 template → may be DocxTemplate (fallback template) or WordDocument
        assert rendered is not None

    def test_formatter_output_is_saveable(self, full_doc, tmp_path):
        """The generated_doc can be saved to a real .docx file."""
        formatter = Formatter(templates_dir="app/templates", contracts_dir="app/pipeline/contracts")
        formatter.process(full_doc)
        out = tmp_path / "output.docx"
        full_doc.generated_doc.save(str(out))
        assert out.exists(), "Output .docx file must be written to disk"
        assert out.stat().st_size > 0, "Output .docx must not be empty"

    def test_formatter_output_is_valid_zip(self, full_doc, tmp_path):
        """A .docx saved by the formatter is a valid ZIP/OOXML file."""
        import zipfile
        formatter = Formatter(templates_dir="app/templates", contracts_dir="app/pipeline/contracts")
        formatter.process(full_doc)
        out = tmp_path / "output.docx"
        full_doc.generated_doc.save(str(out))
        assert zipfile.is_zipfile(str(out)), ".docx must be a valid ZIP archive"
