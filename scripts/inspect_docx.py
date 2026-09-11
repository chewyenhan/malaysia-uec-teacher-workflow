#!/usr/bin/env python3
"""Create a structural first-pass inventory of a DOCX package."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


def text_of(node: ET.Element) -> str:
    return "".join(part.text or "" for part in node.findall(".//w:t", NS)).strip()


def relationship_map(archive: zipfile.ZipFile, part_name: str) -> dict[str, str]:
    part = PurePosixPath(part_name)
    rels_name = str(part.parent / "_rels" / f"{part.name}.rels")
    if rels_name not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read(rels_name))
    return {
        item.get("Id", ""): item.get("Target", "")
        for item in root.findall("rel:Relationship", REL_NS)
        if item.get("Id")
    }


def pictures_of(node: ET.Element, relationships: dict[str, str]) -> list[dict[str, str]]:
    descriptions = [
        {
            "name": item.get("name", ""),
            "title": item.get("title", ""),
            "description": item.get("descr", ""),
        }
        for item in node.findall(".//wp:docPr", NS)
    ]
    pictures = []
    for position, blip in enumerate(node.findall(".//a:blip", NS)):
        relationship_id = blip.get(f"{{{NS['r']}}}embed", "")
        picture = {
            "relationship_id": relationship_id,
            "target": relationships.get(relationship_id, ""),
        }
        if position < len(descriptions):
            picture.update(descriptions[position])
        pictures.append(picture)
    return pictures


def table_rows(node: ET.Element) -> list[list[str]]:
    return [[text_of(cell) for cell in row.findall("w:tc", NS)] for row in node.findall("w:tr", NS)]


def ancillary_part_inventory(archive: zipfile.ZipFile, part_name: str) -> dict:
    root = ET.fromstring(archive.read(part_name))
    relationships = relationship_map(archive, part_name)
    return {
        "part": part_name,
        "text": text_of(root),
        "paragraphs": len(root.findall(".//w:p", NS)),
        "tables": [table_rows(table) for table in root.findall(".//w:tbl", NS)],
        "drawings": len(root.findall(".//w:drawing", NS)),
        "pictures": pictures_of(root, relationships),
    }


def inventory(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        root = ET.fromstring(archive.read("word/document.xml"))
        relationships = relationship_map(archive, "word/document.xml")
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
                    "pictures": pictures_of(child, relationships),
                })
            elif kind == "tbl":
                table_count += 1
                items.append({
                    "type": "table",
                    "index": table_count,
                    "rows": table_rows(child),
                    "drawings": len(child.findall(".//w:drawing", NS)),
                    "pictures": pictures_of(child, relationships),
                })
        media = sorted(name for name in names if name.startswith("word/media/"))
        ancillary_names = sorted(
            name for name in names
            if name.startswith("word/")
            and (
                PurePosixPath(name).name.startswith(("header", "footer"))
                or PurePosixPath(name).name in {"footnotes.xml", "endnotes.xml", "comments.xml"}
            )
            and name.endswith(".xml")
        )
        ancillary = [ancillary_part_inventory(archive, name) for name in ancillary_names]
    return {
        "file": str(path.resolve()),
        "main_body_paragraphs": paragraph_count,
        "main_body_tables": table_count,
        "main_body_drawings": len(root.findall(".//w:drawing", NS)),
        "main_body_pictures": pictures_of(root, relationships),
        "media_files": media,
        "items_in_document_order": items,
        "ancillary_parts": ancillary,
        "limitations": [
            "This is a structural inventory, not a rendered-page inspection.",
            "Visually inspect page layout, captions, cropping, equations and reading order before teaching.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true", help="Allow replacing an existing JSON output file")
    args = parser.parse_args()
    result = inventory(args.docx)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        if args.output.exists() and not args.force:
            parser.error(f"output already exists (use --force to replace): {args.output}")
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
