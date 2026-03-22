#!/usr/bin/env python3
"""Run ESLint only on staged frontend files passed by pre-commit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from shutil import which


VALID_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx"}
FRONTEND_PREFIX = Path("frontend")


def _normalize_for_eslint(path: str) -> str:
    return path.replace("\\", "/")


def main(argv: list[str]) -> int:
    candidate_files: list[str] = []
    for raw in argv:
        file_path = Path(raw)
        if file_path.suffix.lower() not in VALID_EXTENSIONS:
            continue
        if not str(file_path).startswith(str(FRONTEND_PREFIX)):
            continue
        if not file_path.exists():
            # Deleted/renamed files can still appear in staged filenames.
            continue
        candidate_files.append(_normalize_for_eslint(str(file_path)))

    if not candidate_files:
        return 0

    npm_executable = which("npm") or which("npm.cmd")
    if not npm_executable:
        print("frontend-eslint: npm is not installed or not on PATH.", file=sys.stderr)
        return 1

    command = [
        npm_executable,
        "--prefix",
        "frontend",
        "exec",
        "--",
        "eslint",
        "--max-warnings",
        "0",
        *candidate_files,
    ]

    result = subprocess.run(command, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
