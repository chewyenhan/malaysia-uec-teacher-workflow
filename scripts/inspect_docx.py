#!/usr/bin/env python3
"""Inventory paragraphs, tables, drawings and relationships in a DOCX file."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def text_of(node: ET.Element) -> str:
    return "".join(part.text or "" for part in node.findall(".//w:t", NS)).strip()


def inventory(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        body = root.find("w:body", NS)
        if body is None:
            raise ValueError("DOCX has no document body")
        items: list[dict] = []
        table_count = 0
        paragraph_count = 0
        for child in list(body):
            kind = child.tag.rsplit("}", 1)[-1]
            if kind == "p":
                paragraph_count += 1
                style = child.find("w:pPr/w:pStyle", NS)
                items.append({
                    "type": "paragraph",
                    "index": paragraph_count,
                    "style": style.get(f"{{{NS['w']}}}val") if style is not None else "",
                    "text": text_of(child),
                    "drawings": len(child.findall(".//w:drawing", NS)),
                })
            elif kind == "tbl":
                table_count += 1
                rows = []
                for row in child.findall("w:tr", NS):
                    rows.append([text_of(cell) for cell in row.findall("w:tc", NS)])
                items.append({"type": "table", "index": table_count, "rows": rows})
        media = sorted(name for name in archive.namelist() if name.startswith("word/media/"))
    return {
        "file": str(path.resolve()),
        "paragraphs": paragraph_count,
        "tables": table_count,
        "media_files": media,
        "items_in_document_order": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inventory(args.docx)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

