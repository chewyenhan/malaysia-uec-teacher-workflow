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
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ALLOWED_HOSTS = {"dongzong.my", "www.dongzong.my", "uec.dongzong.my"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
MAX_BYTES = 60 * 1024 * 1024
USER_AGENT = "malaysia-uec-teacher-workflow/0.1 (+https://github.com/chewyenhan/malaysia-uec-teacher-workflow)"


class OfficialOnlyRedirectHandler(HTTPRedirectHandler):
    """Reject redirects that leave the official Dong Zong host allowlist."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        absolute = urljoin(req.full_url, newurl)
        if not allowed_url(absolute):
            raise ValueError(f"Blocked redirect to non-official URL: {absolute}")
        return super().redirect_request(req, fp, code, msg, headers, absolute)


OPENER = build_opener(OfficialOnlyRedirectHandler())


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


def fetch_bytes(url: str, max_bytes: int = MAX_BYTES, attempts: int = 3) -> bytes:
    if not allowed_url(url):
        raise ValueError(f"Blocked non-official URL: {url}")
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(1, attempts + 1):
        request = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with OPENER.open(request, timeout=30) as response:
                final_url = response.geturl()
                if not allowed_url(final_url):
                    raise ValueError(f"Blocked final non-official URL: {final_url}")
                length = response.headers.get("Content-Length")
                if length and int(length) > max_bytes:
                    raise ValueError(f"File exceeds {max_bytes} bytes: {url}")
                data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise ValueError(f"File exceeds {max_bytes} bytes: {url}")
            return data
        except HTTPError as exc:
            if exc.code < 500 or attempt == attempts:
                raise
        except (URLError, TimeoutError, ConnectionResetError, OSError):
            if attempt == attempts:
                raise
        time.sleep(0.5 * attempt)
    raise RuntimeError("unreachable")


def safe_filename(url: str, label: str, index: int) -> str:
    raw = Path(unquote(urlparse(url).path)).name or f"document-{index}.pdf"
    raw = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", raw).strip(" .")
    if not raw:
        raw = f"document-{index}.pdf"
    if len(raw) > 140:
        suffix = Path(raw).suffix
        raw = raw[: 140 - len(suffix)] + suffix
    return raw


def unique_destination(directory: Path, url: str, label: str, index: int, used: dict[str, str]) -> Path:
    """Return a stable path without silently colliding with another URL."""
    filename = safe_filename(url, label, index)
    key = filename.casefold()
    if key in used and used[key] != url:
        suffix = Path(filename).suffix
        stem = filename[: -len(suffix)] if suffix else filename
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
        filename = f"{stem}-{digest}{suffix}"
        key = filename.casefold()
    used[key] = url
    return directory / filename


def validate_document_payload(url: str, payload: bytes) -> None:
    """Reject an HTML/error response masquerading as an office document."""
    suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    signatures = {
        ".pdf": (b"%PDF",),
        ".docx": (b"PK\x03\x04",),
        ".xlsx": (b"PK\x03\x04",),
        ".doc": (b"\xd0\xcf\x11\xe0",),
        ".xls": (b"\xd0\xcf\x11\xe0",),
    }
    expected = signatures.get(suffix)
    if expected and not any(payload.startswith(signature) for signature in expected):
        raise ValueError(f"Downloaded content does not match {suffix} format: {url}")


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
        "status": "partial",
        "levels": [],
        "documents": [],
        "errors": [],
    }
    used_destinations: dict[str, dict[str, str]] = {}

    for index in indexes:
        level_record = {
            "level": index["level"],
            "index_url": index["url"],
            "expected_subject_count": index.get("expected_subject_count"),
            "discovered_subject_count": 0,
            "subjects_with_documents": 0,
            "document_count": 0,
            "status": "partial",
        }
        manifest["levels"].append(level_record)
        print(f"Checking {index['title']}: {index['url']}")
        try:
            page = fetch_bytes(index["url"], max_bytes=5 * 1024 * 1024).decode("utf-8", errors="replace")
        except Exception as exc:
            print(f"ERROR: unable to read official index: {exc}", file=sys.stderr)
            manifest["errors"].append({"level": index["level"], "url": index["url"], "error": str(exc)})
            continue
        documents = discover_documents(index["url"], page)
        subject_pages = discover_subject_pages(index["url"], page, index["level"])
        level_record["discovered_subject_count"] = len(subject_pages)
        print(f"  discovered {len(subject_pages)} subject pages")
        expected = index.get("expected_subject_count")
        if expected is not None and len(subject_pages) != expected:
            message = f"expected {expected} subjects but found {len(subject_pages)}"
            manifest["errors"].append({"level": index["level"], "url": index["url"], "error": message})
            print(f"  ERROR: {message}", file=sys.stderr)
        by_url = {item["url"]: item for item in documents}
        for subject in subject_pages:
            try:
                subject_html = fetch_bytes(subject["url"], max_bytes=5 * 1024 * 1024).decode("utf-8", errors="replace")
            except Exception as exc:
                print(f"  ERROR unable to read {subject['label']}: {exc}", file=sys.stderr)
                manifest["errors"].append({"level": index["level"], "subject": subject["label"], "url": subject["url"], "error": str(exc)})
                continue
            subject_documents = discover_documents(subject["url"], subject_html)
            if not subject_documents:
                message = "no official document discovered on subject page"
                manifest["errors"].append({"level": index["level"], "subject": subject["label"], "url": subject["url"], "error": message})
                print(f"  ERROR {subject['label']}: {message}", file=sys.stderr)
                continue
            level_record["subjects_with_documents"] += 1
            for document in subject_documents:
                document["subject"] = subject["label"]
                document["detail_url"] = subject["url"]
                by_url[document["url"]] = document
        documents = [by_url[url] for url in sorted(by_url)]
        level_record["document_count"] = len(documents)
        print(f"  discovered {len(documents)} official documents")
        level_errors = [error for error in manifest["errors"] if error.get("level") == index["level"]]
        if level_record["subjects_with_documents"] == len(subject_pages) and not level_errors:
            level_record["status"] = "complete"
        level_destinations = used_destinations.setdefault(index["level"], {})
        for number, document in enumerate(documents, start=1):
            record = {**document, "level": index["level"], "index_url": index["url"]}
            if args.list_only:
                subject_label = document.get("subject") or document["label"] or "(untitled)"
                print(f"  - {subject_label}: {document['url']}")
            else:
                try:
                    payload = fetch_bytes(document["url"])
                    validate_document_payload(document["url"], payload)
                    level_dir = args.cache_dir / index["level"]
                    level_dir.mkdir(parents=True, exist_ok=True)
                    destination = unique_destination(
                        level_dir, document["url"], document["label"], number, level_destinations
                    )
                    temporary = destination.with_name(destination.name + ".part")
                    try:
                        temporary.write_bytes(payload)
                        temporary.replace(destination)
                    finally:
                        if temporary.exists():
                            temporary.unlink()
                    record.update({
                        "path": str(destination.resolve()),
                        "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    })
                    print(f"  saved {destination.name}")
                except Exception as exc:
                    record["error"] = str(exc)
                    level_record["status"] = "partial"
                    manifest["errors"].append({"level": index["level"], "url": document["url"], "error": str(exc)})
                    print(f"  ERROR {document['url']}: {exc}", file=sys.stderr)
            manifest["documents"].append(record)

    manifest["status"] = "complete" if manifest["documents"] and not manifest["errors"] else "partial"
    if not args.list_only:
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = args.cache_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Manifest: {manifest_path}")

    if manifest["status"] != "complete":
        print("Syllabus sync is incomplete. Review manifest errors and the official index pages.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
