from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from app.pipeline.export.latex_exporter import LaTeXExporter


def test_convert_to_latex_requires_pandoc(tmp_path: Path):
    docx_path = tmp_path / "input.docx"
    docx_path.write_bytes(b"PK\x03\x04")
    exporter = LaTeXExporter()

    with patch("app.pipeline.export.latex_exporter.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="Pandoc is not installed"):
            exporter.convert_to_latex(str(docx_path), str(tmp_path))


def test_convert_to_latex_invokes_pandoc_and_returns_output(tmp_path: Path):
    docx_path = tmp_path / "paper.docx"
    docx_path.write_bytes(b"PK\x03\x04")
    output_dir = tmp_path / "out"
    output_path = output_dir / "paper.tex"
    exporter = LaTeXExporter(timeout_seconds=10)

    def _fake_run(*args, **kwargs):
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\\section{Intro}", encoding="utf-8")
        return subprocess.CompletedProcess(args=kwargs.get("args", []), returncode=0)

    with (
        patch("app.pipeline.export.latex_exporter.shutil.which", return_value="pandoc"),
        patch("app.pipeline.export.latex_exporter.subprocess.run", side_effect=_fake_run) as run_mock,
    ):
        result = exporter.convert_to_latex(str(docx_path), str(output_dir))

    assert result == str(output_path)
    assert output_path.exists()
    called_command = run_mock.call_args.args[0]
    assert "--to=latex" in called_command
    assert "--standalone" in called_command


def test_convert_to_latex_surfaces_pandoc_failure(tmp_path: Path):
    docx_path = tmp_path / "paper.docx"
    docx_path.write_bytes(b"PK\x03\x04")
    exporter = LaTeXExporter()

    with (
        patch("app.pipeline.export.latex_exporter.shutil.which", return_value="pandoc"),
        patch(
            "app.pipeline.export.latex_exporter.subprocess.run",
            return_value=subprocess.CompletedProcess(args=["pandoc"], returncode=2, stderr="bad input"),
        ),
    ):
        with pytest.raises(RuntimeError, match="Pandoc failed"):
            exporter.convert_to_latex(str(docx_path), str(tmp_path / "out"))
