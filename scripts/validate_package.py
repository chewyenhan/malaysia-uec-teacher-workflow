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
}


def main() -> int:
    errors: list[str] = []
    for relative in sorted(REQUIRED):
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    text_files = [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.resolve() != Path(__file__).resolve()
        and path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml"}
    ]
    for path in text_files:
        content = path.read_text(encoding="utf-8")
        for pattern, label in FORBIDDEN.items():
            if re.search(pattern, content, flags=re.IGNORECASE):
                errors.append(f"{path.relative_to(ROOT)} contains {label}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8") if (ROOT / "SKILL.md").exists() else ""
    if "name: malaysia-uec-teacher-workflow" not in skill:
        errors.append("SKILL.md name does not match repository")

    total = len(REQUIRED) + len(text_files) + 1
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"Result: {total - len(errors)}/{total} checks passed")
        return 1
    print(f"Result: {total}/{total} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
