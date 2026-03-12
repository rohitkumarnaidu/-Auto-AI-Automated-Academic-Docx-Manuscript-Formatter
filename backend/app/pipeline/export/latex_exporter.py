from __future__ import annotations

import os
import shutil
import subprocess


class LaTeXExporter:
    """Convert generated DOCX files into LaTeX with Pandoc."""

    def convert_to_latex(self, docx_path: str, output_dir: str) -> str:
        if not shutil.which("pandoc"):
            raise RuntimeError("Pandoc is not installed")

        os.makedirs(output_dir, exist_ok=True)
        output_name = f"{os.path.splitext(os.path.basename(docx_path))[0]}.tex"
        output_path = os.path.join(output_dir, output_name)

        subprocess.run(
            ["pandoc", docx_path, "-o", output_path],
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
        )
        return output_path
