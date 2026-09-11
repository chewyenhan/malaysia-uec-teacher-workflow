#!/usr/bin/env python3
"""Discover and cache official Dong Zong UEC syllabus documents.

The repository stores only official index URLs. This script discovers linked
documents at run time, restricts downloads to Dong Zong domains, and writes a
local provenance manifest with hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

ALLOWED_HOSTS = {"dongzong.my", "www.dongzong.my", "uec.dongzong.my"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
MAX_BYTES = 60 * 1024 * 1024
USER_AGENT = "malaysia-uec-teacher-workflow/0.1 (+https://github.com/chewyenhan/malaysia-uec-teacher-workflow)"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        values = dict(attrs)
        self._href = values.get("href")
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._text).strip()))
            self._href = None
            self._text = []


def allowed_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and (parsed.hostname or "").lower() in ALLOWED_HOSTS


def discover_documents(page_url: str, page_html: str) -> list[dict[str, str]]:
    parser = LinkParser()
    parser.feed(page_html)
    found: dict[str, dict[str, str]] = {}
    for href, label in parser.links:
        absolute = urljoin(page_url, html.unescape(href))
        suffix = Path(unquote(urlparse(absolute).path)).suffix.lower()
        if suffix not in DOCUMENT_EXTENSIONS or not allowed_url(absolute):
            continue
        found[absolute] = {"url": absolute, "label": re.sub(r"\s+", " ", label).strip()}
    # Dong Zong's PDF viewer stores the document URL in plugin markup rather
    # than a clickable <a>. Inspect official page source for those URLs too.
    normalized = html.unescape(page_html).replace(r"\/", "/")
    candidates = re.findall(
        r"https?://[^\"'<>\s]+?\.(?:pdf|docx?|xlsx?)(?:\?[^\"'<>\s]*)?",
        normalized,
        flags=re.IGNORECASE,
    )
    for candidate in candidates:
        absolute = candidate.rstrip("),;]")
        if allowed_url(absolute):
            found.setdefault(absolute, {"url": absolute, "label": Path(unquote(urlparse(absolute).path)).name})
    return [found[url] for url in sorted(found)]


def discover_subject_pages(page_url: str, page_html: str, level: str) -> list[dict[str, str]]:
    parser = LinkParser()
    parser.feed(page_html)
    prefix = "初中" if level == "junior" else "高中"
    expected_category = "8" if level == "junior" else "7"
    found: dict[str, dict[str, str]] = {}
    for position, (href, label) in enumerate(parser.links):
        absolute = urljoin(page_url, html.unescape(href))
        parsed = urlparse(absolute)
        if not allowed_url(absolute) or "p" not in parse_qs(parsed.query):
            continue
        cleaned_label = re.sub(r"\s+", " ", label).strip()
        next_query = {}
        if position + 1 < len(parser.links):
            next_url = urljoin(page_url, html.unescape(parser.links[position + 1][0]))
            next_query = parse_qs(urlparse(next_url).query)
        if cleaned_label.startswith(prefix) and next_query.get("cat") == [expected_category]:
            found[absolute] = {"url": absolute, "label": cleaned_label}
    return [found[url] for url in sorted(found)]


def fetch_bytes(url: str, max_bytes: int = MAX_BYTES) -> bytes:
    if not allowed_url(url):
        raise ValueError(f"Blocked non-official URL: {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > max_bytes:
            raise ValueError(f"File exceeds {max_bytes} bytes: {url}")
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"File exceeds {max_bytes} bytes: {url}")
    return data


def safe_filename(url: str, label: str, index: int) -> str:
    raw = Path(unquote(urlparse(url).path)).name or f"document-{index}.pdf"
    raw = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", raw).strip(" .")
    if not raw:
        raw = f"document-{index}.pdf"
    if len(raw) > 140:
        suffix = Path(raw).suffix
        raw = raw[: 140 - len(suffix)] + suffix
    return raw


def load_sources(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", choices=("junior", "senior", "all"), default="all")
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".uec-teacher-workflow" / "syllabi")
    parser.add_argument("--sources", type=Path, default=Path(__file__).resolve().parents[1] / "references" / "official-sources.json")
    parser.add_argument("--list-only", action="store_true", help="Discover links without downloading documents")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_sources(args.sources)
    indexes = [item for item in config["syllabus_indexes"] if args.level in ("all", item["level"])]
    manifest: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "publisher": config["publisher"],
        "documents": [],
    }

    for index in indexes:
        print(f"Checking {index['title']}: {index['url']}")
        try:
            page = fetch_bytes(index["url"], max_bytes=5 * 1024 * 1024).decode("utf-8", errors="replace")
        except Exception as exc:
            print(f"ERROR: unable to read official index: {exc}", file=sys.stderr)
            continue
        documents = discover_documents(index["url"], page)
        subject_pages = discover_subject_pages(index["url"], page, index["level"])
        print(f"  discovered {len(subject_pages)} subject pages")
        by_url = {item["url"]: item for item in documents}
        for subject in subject_pages:
            try:
                subject_html = fetch_bytes(subject["url"], max_bytes=5 * 1024 * 1024).decode("utf-8", errors="replace")
            except Exception as exc:
                print(f"  ERROR unable to read {subject['label']}: {exc}", file=sys.stderr)
                continue
            for document in discover_documents(subject["url"], subject_html):
                document["subject"] = subject["label"]
                document["detail_url"] = subject["url"]
                by_url[document["url"]] = document
        documents = [by_url[url] for url in sorted(by_url)]
        print(f"  discovered {len(documents)} official documents")
        for number, document in enumerate(documents, start=1):
            record = {**document, "level": index["level"], "index_url": index["url"]}
            if args.list_only:
                subject_label = document.get("subject") or document["label"] or "(untitled)"
                print(f"  - {subject_label}: {document['url']}")
            else:
                try:
                    payload = fetch_bytes(document["url"])
                    level_dir = args.cache_dir / index["level"]
                    level_dir.mkdir(parents=True, exist_ok=True)
                    destination = level_dir / safe_filename(document["url"], document["label"], number)
                    destination.write_bytes(payload)
                    record.update({
                        "path": str(destination.resolve()),
                        "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    })
                    print(f"  saved {destination.name}")
                except Exception as exc:
                    record["error"] = str(exc)
                    print(f"  ERROR {document['url']}: {exc}", file=sys.stderr)
            manifest["documents"].append(record)

    if not args.list_only:
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = args.cache_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Manifest: {manifest_path}")

    if not manifest["documents"]:
        print("No documents were discovered. Open the official index URLs manually; their page structure may have changed.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
