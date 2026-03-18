from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class LaTeXExporter:
    """Convert generated DOCX files into LaTeX using Pandoc."""

    def __init__(self, timeout_seconds: int = 120):
        self.timeout_seconds = int(timeout_seconds)

    @staticmethod
    def _resolve_pandoc_binary() -> Optional[str]:
        configured_path = (os.getenv("PANDOC_PATH") or "").strip()
        if configured_path:
            return configured_path
        return shutil.which("pandoc")

    def convert_to_latex(self, docx_path: str, output_dir: str) -> str:
        source_path = Path(docx_path)
        if not source_path.exists():
            raise RuntimeError(f"DOCX source not found: {docx_path}")

        pandoc_binary = self._resolve_pandoc_binary()
        if not pandoc_binary:
            raise RuntimeError(
                "Pandoc is not installed. Install Pandoc or set PANDOC_PATH to the binary location."
            )

        output_root = Path(output_dir)
        output_root.mkdir(parents=True, exist_ok=True)
        output_path = output_root / f"{source_path.stem}.tex"

        command = [
            pandoc_binary,
            str(source_path),
            "--from=docx",
            "--to=latex",
            "--standalone",
            "--output",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                command,
                check=False,
                timeout=self.timeout_seconds,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Pandoc timed out after {self.timeout_seconds}s while converting '{docx_path}'."
            ) from exc
        except OSError as exc:
            raise RuntimeError(f"Failed to execute Pandoc: {exc}") from exc

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            diagnostic = stderr or stdout or "unknown error"
            raise RuntimeError(f"Pandoc failed (exit {result.returncode}): {diagnostic}")

        if not output_path.exists():
            raise RuntimeError("Pandoc reported success but no .tex output was created.")

        logger.info("LaTeX export completed: %s", output_path)
        return str(output_path)
