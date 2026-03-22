#!/usr/bin/env python3
"""Generate .env.template files from code usage and .env.example defaults.

Usage:
    python scripts/generate_env_template.py
    python scripts/generate_env_template.py --sync-examples
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_DIR = ROOT_DIR / "backend"

IGNORE_DIRS = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}

FRONTEND_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".html"}
BACKEND_EXTENSIONS = {".py"}

FRONTEND_PATTERNS = [
    re.compile(r"process\.env\.([A-Z][A-Z0-9_]+)"),
    re.compile(r"import\.meta\.env\.([A-Z][A-Z0-9_]+)"),
]

BACKEND_PATTERNS = [
    re.compile(r"_require_env\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]\s*\)"),
    re.compile(r"os\.getenv\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]"),
    re.compile(r"os\.environ\.get\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]"),
    re.compile(r"os\.environ\[\s*['\"]([A-Z][A-Z0-9_]+)['\"]\s*\]"),
    re.compile(r"Field\([^)]*env\s*=\s*['\"]([A-Z][A-Z0-9_]+)['\"]"),
]

ENV_ASSIGN_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]+)\s*=\s*(.*)$")
AUTO_SECTION_MARKERS = {
    "# Automatically discovered variables",
    "# Auto-discovered keys without defaults",
}
IGNORED_ENV_NAMES = {
    "BASE_URL",
    "CI",
    "DEV",
    "HF_HUB_DISABLE_PROGRESS_BARS",
    "HF_HUB_DISABLE_SYMLINKS_WARNING",
    "MODE",
    "NODE_ENV",
    "PROD",
    "PYTEST_CURRENT_TEST",
    "SSR",
}


def _iter_files(root: Path, allowed_extensions: set[str]) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix in allowed_extensions:
                files.append(path)
    return files


def _scan_env_names(root: Path, patterns: list[re.Pattern[str]], allowed_extensions: set[str]) -> set[str]:
    found: set[str] = set()
    for path in _iter_files(root, allowed_extensions):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in patterns:
            found.update(pattern.findall(content))
    return {name for name in found if name not in IGNORED_ENV_NAMES}


def _extract_settings_class_fields(settings_path: Path) -> set[str]:
    """Extract uppercase Settings class fields from backend settings.py."""
    try:
        lines = settings_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return set()

    names: set[str] = set()
    in_settings_class = False
    class_indent = 0

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        if re.match(r"^\s*class\s+Settings\b", line):
            in_settings_class = True
            class_indent = indent
            continue

        if in_settings_class and stripped and indent <= class_indent and not stripped.startswith("@"):
            in_settings_class = False

        if not in_settings_class:
            continue

        match = re.match(r"^\s*([A-Z][A-Z0-9_]+)\s*:", line)
        if match:
            name = match.group(1)
            if name not in IGNORED_ENV_NAMES:
                names.add(name)

    return names


def _remove_auto_discovered_section(lines: list[str]) -> list[str]:
    for idx, line in enumerate(lines):
        if line.strip() in AUTO_SECTION_MARKERS:
            return lines[:idx]
    return lines


def _extract_assigned_keys(lines: list[str]) -> set[str]:
    keys: set[str] = set()
    for line in lines:
        match = ENV_ASSIGN_RE.match(line)
        if match:
            keys.add(match.group(1))
    return keys


def _render_template(base_lines: list[str], missing_keys: list[str]) -> str:
    cleaned_lines = _remove_auto_discovered_section(base_lines)
    while cleaned_lines and cleaned_lines[-1].strip() == "":
        cleaned_lines.pop()

    output_lines = list(cleaned_lines)
    if missing_keys:
        output_lines.append("")
        output_lines.append("# Auto-discovered keys without defaults")
        output_lines.extend(f"{key}=" for key in missing_keys)

    return "\n".join(output_lines).rstrip() + "\n"


def _write_if_changed(path: Path, content: str) -> bool:
    current = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else None
    if current == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _load_base_lines(example_path: Path, project_name: str) -> list[str]:
    if example_path.exists():
        return example_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return [f"# {project_name} environment template"]


def _generate_project_template(
    *,
    project_name: str,
    project_dir: Path,
    patterns: list[re.Pattern[str]],
    allowed_extensions: set[str],
    example_path: Path,
    template_path: Path,
    extra_discovered: set[str] | None = None,
    sync_examples: bool = False,
) -> tuple[int, bool, bool]:
    discovered = _scan_env_names(project_dir, patterns, allowed_extensions)
    if extra_discovered:
        discovered.update(extra_discovered)
    discovered = {key for key in discovered if key not in IGNORED_ENV_NAMES}

    base_lines = _load_base_lines(example_path, project_name)
    existing_keys = _extract_assigned_keys(_remove_auto_discovered_section(base_lines))
    missing_keys = sorted(key for key in discovered if key not in existing_keys)

    rendered = _render_template(base_lines, missing_keys)
    template_changed = _write_if_changed(template_path, rendered)

    example_changed = False
    if sync_examples:
        example_changed = _write_if_changed(example_path, rendered)

    return len(missing_keys), template_changed, example_changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate backend/frontend .env.template files from code usage and .env.example defaults."
    )
    parser.add_argument(
        "--sync-examples",
        action="store_true",
        help="Also update backend/.env.example and frontend/.env.example with discovered keys.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    backend_settings_vars = _extract_settings_class_fields(BACKEND_DIR / "app" / "config" / "settings.py")
    backend_missing, backend_template_changed, backend_example_changed = _generate_project_template(
        project_name="Backend",
        project_dir=BACKEND_DIR,
        patterns=BACKEND_PATTERNS,
        allowed_extensions=BACKEND_EXTENSIONS,
        example_path=BACKEND_DIR / ".env.example",
        template_path=BACKEND_DIR / ".env.template",
        extra_discovered=backend_settings_vars,
        sync_examples=args.sync_examples,
    )

    frontend_missing, frontend_template_changed, frontend_example_changed = _generate_project_template(
        project_name="Frontend",
        project_dir=FRONTEND_DIR,
        patterns=FRONTEND_PATTERNS,
        allowed_extensions=FRONTEND_EXTENSIONS,
        example_path=FRONTEND_DIR / ".env.example",
        template_path=FRONTEND_DIR / ".env.template",
        sync_examples=args.sync_examples,
    )

    print(
        "Generated templates:\n"
        f"- backend/.env.template ({backend_missing} auto-discovered key(s); changed={backend_template_changed})\n"
        f"- frontend/.env.template ({frontend_missing} auto-discovered key(s); changed={frontend_template_changed})"
    )

    if args.sync_examples:
        print(
            "Synced examples:\n"
            f"- backend/.env.example changed={backend_example_changed}\n"
            f"- frontend/.env.example changed={frontend_example_changed}"
        )


if __name__ == "__main__":
    main()
