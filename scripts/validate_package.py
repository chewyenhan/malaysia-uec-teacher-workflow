#!/usr/bin/env python3
"""Check package structure and guard against personal-path leakage."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "SKILL.md",
    "README.md",
    "LICENSE.md",
    "NOTICE.md",
    "agents/openai.yaml",
    "references/official-sources.json",
    "evals/evals.json",
}
FORBIDDEN = {
    r"D:\\AIgames": "private workspace path",
    r"junior-history-lesson": "personal skill dependency",
    r"2026 lesson plan": "personal workbook name",
    r"J1Y": "personal class identifier",
    r"[A-Za-z]:\\Users\\": "Windows user-profile path",
    r"/(?:Users|home)/[^/\s]+/": "user-profile path",
    r"(?:^|[/\\])\.claude(?:[/\\])": "private assistant configuration path",
    r"(?:^|[/\\])\.agents(?:[/\\])": "private assistant configuration path",
}
SECRET_PATTERNS = {
    r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b": "GitHub token",
    r"\bgithub_pat_[A-Za-z0-9_]{20,}\b": "GitHub fine-grained token",
    r"\bAIza[A-Za-z0-9_-]{30,}\b": "Google API key",
    r"\bsk-[A-Za-z0-9_-]{20,}\b": "API key",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----": "private key",
}
JUNK_DIRECTORY_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
MAX_REPOSITORY_FILE_BYTES = 5 * 1024 * 1024


def main() -> int:
    errors: list[str] = []
    for relative in sorted(REQUIRED):
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    all_files = [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
    ]
    text_files = [
        path for path in all_files
        if path.resolve() != Path(__file__).resolve()
        and path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml", ".cff"}
    ]
    for path in text_files:
        content = path.read_text(encoding="utf-8")
        for pattern, label in FORBIDDEN.items():
            if re.search(pattern, content, flags=re.IGNORECASE):
                errors.append(f"{path.relative_to(ROOT)} contains {label}")
        for pattern, label in SECRET_PATTERNS.items():
            if re.search(pattern, content):
                errors.append(f"{path.relative_to(ROOT)} contains possible {label}")

    for path in all_files:
        if path.stat().st_size > MAX_REPOSITORY_FILE_BYTES:
            errors.append(f"{path.relative_to(ROOT)} exceeds the 5 MiB repository limit")

    junk_directories = sorted(
        path.relative_to(ROOT) for path in ROOT.rglob("*")
        if path.is_dir() and ".git" not in path.parts and path.name in JUNK_DIRECTORY_NAMES
    )
    if junk_directories:
        errors.append("junk directories remain: " + ", ".join(map(str, junk_directories)))

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8") if (ROOT / "SKILL.md").exists() else ""
    if "name: malaysia-uec-teacher-workflow" not in skill:
        errors.append("SKILL.md name does not match repository")

    total = (
        len(REQUIRED)
        + len(text_files) * (len(FORBIDDEN) + len(SECRET_PATTERNS))
        + len(all_files)
        + 1  # no junk directories
        + 1  # skill name
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"Result: {total - len(errors)}/{total} checks passed")
        return 1
    print(f"Result: {total}/{total} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
