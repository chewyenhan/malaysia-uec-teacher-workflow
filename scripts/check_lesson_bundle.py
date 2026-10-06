#!/usr/bin/env python3
"""Read-only structural checks for a lesson's task record and local outputs.

No network, third-party dependencies, authentication, writes, or deletions.
Content and visual QA remain separate teacher/agent checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def page_ids(text: str) -> list[str]:
    table = re.findall(r"^\|\s*(P\d{2,})\s*\|", text, re.MULTILINE)
    return table or re.findall(r"^#{1,6}\s+(P\d{2,})\b", text, re.MULTILINE)


def pptx_page_count(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        required = {"[Content_Types].xml", "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels"}
        if not required.issubset(archive.namelist()):
            raise ValueError("required PowerPoint parts are missing")
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        relationships = ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
        rels = {item.get("Id"): item for item in relationships}
        slides = presentation.findall(f"{{{P_NS}}}sldIdLst/{{{P_NS}}}sldId")
        if not slides:
            raise ValueError("presentation has no slides")
        for slide in slides:
            rel = rels.get(slide.get(f"{{{R_NS}}}id"))
            if rel is None or rel.get("TargetMode") == "External":
                raise ValueError("slide relationship is missing or external")
            target = rel.get("Target", "")
            if not target:
                raise ValueError("slide target is missing")
            # Resolve ZIP member names, without opening any external paths.
            member_parts: list[str] = [] if target.startswith("/") else ["ppt"]
            for part in target.split("/"):
                if part in {"", "."}:
                    continue
                if part == "..":
                    if not member_parts:
                        raise ValueError("slide target escapes archive root")
                    member_parts.pop()
                else:
                    member_parts.append(part)
            member = "/".join(member_parts)
            if member not in archive.namelist():
                raise ValueError("referenced slide is missing")
            if ET.fromstring(archive.read(member)).tag != f"{{{P_NS}}}sld":
                raise ValueError("referenced part is not a slide")
        return len(slides)


def validate_bundle(folder: Path, manifest_name: str = "task-state.json", require_complete: bool = False) -> dict:
    checks: list[dict] = []
    warnings: list[str] = []

    def check(label: str, passed: bool) -> None:
        checks.append({"check": label, "passed": bool(passed)})

    def finish() -> dict:
        passed = sum(item["passed"] for item in checks)
        return {
            "scope": "local structure only; not content, visual, or live-service QA",
            "passed": passed, "total": len(checks),
            "ok": passed == len(checks),
            "checks": checks, "warnings": warnings,
        }

    try:
        state = json.loads((folder / manifest_name).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        check("task record is readable JSON", False)
        return finish()
    check("task record is an object", isinstance(state, dict))
    if not isinstance(state, dict):
        return finish()
    check("schema version is supported", state.get("schema_version") == 1)
    check("curriculum route is uec or custom", state.get("curriculum_route") in {"uec", "custom"}
          if isinstance(state.get("curriculum_route"), str) else False)
    route = state.get("slide_route")
    valid_route = route in {"editable", "notebooklm", "outline-only", None} if isinstance(route, (str, type(None))) else False
    check("slide route is supported", valid_route)
    if not valid_route:
        return finish()
    sources = state.get("sources")
    check("source mapping is an object", isinstance(sources, dict))
    if not isinstance(sources, dict):
        return finish()

    required = (("material", "lesson_plan", "outline", "teacher_notes") if route == "notebooklm"
                else ("lesson_plan", "outline", "teacher_notes") if route == "editable" else ())
    paths: dict[str, Path] = {}
    for role in required:
        check(f"source role {role} is mapped", isinstance(sources.get(role), str) and bool(sources[role].strip()))
    for role, value in sources.items():
        if not isinstance(value, str) or not value.strip():
            check(f"source {role} has a path", False)
            continue
        try:
            path = (folder / value).resolve()
            present = path.is_file() and path.stat().st_size > 0
        except (OSError, ValueError):
            present = False
            path = None
        check(f"source {role} exists and is nonempty", present)
        if present:
            paths[role] = path
    if route == "notebooklm":
        role_paths = [paths[role] for role in required if role in paths]
        check("four roles use four distinct files", len(role_paths) == 4 and len(set(role_paths)) == 4)

    declared = state.get("page_ids", [])
    check("page IDs are a list of P-number strings",
          isinstance(declared, list) and all(isinstance(item, str) and re.fullmatch(r"P\d{2,}", item) for item in declared))
    if not isinstance(declared, list) or not all(isinstance(item, str) for item in declared):
        return finish()
    check("declared page IDs are unique", len(declared) == len(set(declared)))
    if route in {"editable", "notebooklm", "outline-only"}:
        check("planned page IDs are present", bool(declared))
    if declared:
        for role in ("outline", "teacher_notes"):
            check(f"{role} available for page matching", role in paths)
            if role in paths:
                try:
                    actual = page_ids(paths[role].read_text(encoding="utf-8-sig"))
                except (OSError, UnicodeError):
                    actual = []
                check(f"{role} page order matches task record", actual == declared)

    outputs = state.get("outputs", {})
    check("output mapping is an object", isinstance(outputs, dict))
    steps = state.get("steps", {})
    check("step mapping is an object", isinstance(steps, dict))
    if isinstance(steps, dict):
        allowed = {"pending", "complete", "awaiting_auth", "awaiting_approval", "in_progress", "needs_review", "failed"}
        check("step states are supported", all(isinstance(value, str) and value in allowed for value in steps.values()))
    if isinstance(outputs, dict):
        slide_file = outputs.get("slides")
        if slide_file:
            check("slide output path is a string", isinstance(slide_file, str))
            if isinstance(slide_file, str):
                path = folder / slide_file
                try:
                    if path.suffix.lower() == ".pptx":
                        count = pptx_page_count(path)
                        check("PPTX has real presentation and linked slide parts", True)
                        if declared:
                            check("actual PPTX page count matches plan", count == len(declared))
                    elif path.suffix.lower() == ".pdf":
                        with path.open("rb") as stream:
                            check("PDF has a PDF file signature", stream.read(5) == b"%PDF-")
                    else:
                        check("slide output format is PPTX or PDF", False)
                except (OSError, ValueError, ET.ParseError, zipfile.BadZipFile, KeyError):
                    check("slide output is a valid supported file", False)
        elif isinstance(steps, dict) and steps.get("slides") == "complete":
            check("completed slide step has an actual output", False)
        elif route in {"editable", "notebooklm"}:
            warnings.append("Slides have not been supplied; this is not a completed slide-deck check.")
    if require_complete:
        check("complete bundle uses a PPTX generation route", route in {"editable", "notebooklm"})
        for role in ("lesson_plan", "outline", "teacher_notes"):
            check(f"complete bundle includes {role}", role in paths)
        slide_file = outputs.get("slides") if isinstance(outputs, dict) else None
        check("complete bundle includes PPTX", isinstance(slide_file, str) and Path(slide_file).suffix.lower() == ".pptx")
        for step in ("lesson_plan", "outline", "teacher_notes", "slides", "qa"):
            check(f"complete bundle step {step} is complete", isinstance(steps, dict) and steps.get(step) == "complete")
        qa_file = outputs.get("qa_report") if isinstance(outputs, dict) else None
        try:
            qa_present = isinstance(qa_file, str) and bool(qa_file) and (folder / qa_file).is_file() and (folder / qa_file).stat().st_size > 0
        except (OSError, ValueError):
            qa_present = False
        check("complete bundle has a nonempty QA report", qa_present)
        try:
            sync_path = outputs.get("page_sync") if isinstance(outputs, dict) else None
            sync = json.loads((folder / sync_path).read_text(encoding="utf-8-sig")) if isinstance(sync_path, str) else None
            check("page synchronization record is an object", isinstance(sync, dict))
            if isinstance(sync, dict):
                pages = sync.get("pages")
                valid_pages = isinstance(pages, list) and all(isinstance(item, dict) for item in pages)
                check("synchronization pages are valid", valid_pages)
                if valid_pages:
                    check("synchronization IDs match final page order", [item.get("id") for item in pages] == declared)
                    check("synchronization uses consecutive slide numbers", [item.get("slide_number") for item in pages] == list(range(1, len(declared)+1)))
                    check("every page has matched content and references", all(
                        item.get("status") == "matched" and item.get("outline_ref") == item.get("id")
                        and item.get("notes_ref") == item.get("id")
                        and isinstance(item.get("actual_title"), str) and bool(item["actual_title"].strip())
                        and isinstance(item.get("lesson_plan_ref"), str) and bool(item["lesson_plan_ref"].strip())
                        for item in pages))
                files = sync.get("files", {})
                for role in ("lesson_plan", "outline", "teacher_notes", "slides"):
                    entry = files.get(role) if isinstance(files, dict) else None
                    expected = (folder / slide_file).resolve() if role == "slides" and isinstance(slide_file, str) else paths.get(role)
                    matches = False
                    if isinstance(entry, dict) and expected and isinstance(entry.get("path"), str):
                        actual_path = (folder / entry["path"]).resolve()
                        matches = actual_path == expected and hashlib.sha256(actual_path.read_bytes()).hexdigest() == entry.get("sha256")
                    check(f"synchronization binds current {role} file", matches)
        except (OSError, ValueError, TypeError):
            check("page synchronization record is readable and current", False)

    warnings.append("Check facts, Chinese text, formula accuracy, visual layout, and editability by opening/rendering the actual outputs.")
    return finish()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--manifest", default="task-state.json")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--require-complete", action="store_true", help="Require all four deliverables and recorded QA for final delivery")
    args = parser.parse_args()
    result = validate_bundle(args.folder, args.manifest, args.require_complete)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        for item in result["checks"]:
            print(("PASS: " if item["passed"] else "FAIL: ") + item["check"])
        for warning in result["warnings"]:
            print("NOTE: " + warning)
        print(f"Structure checks: {result['passed']}/{result['total']} passed")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
