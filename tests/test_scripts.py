from pathlib import Path
import argparse
import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib.request import Request
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SyncSyllabiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_script("sync_uec_syllabi.py")

    def test_discovers_only_official_documents(self):
        page = """
        <a href="/files/junior-history.pdf">初中历史考试纲要</a>
        <a href="https://evil.example/textbook.pdf">课本</a>
        <a href="/news">News</a>
        """
        result = self.module.discover_documents("https://uec.dongzong.my/?page_id=479", page)
        self.assertEqual(result, [{
            "url": "https://uec.dongzong.my/files/junior-history.pdf",
            "label": "初中历史考试纲要",
        }])

    def test_blocks_non_official_hosts(self):
        self.assertTrue(self.module.allowed_url("https://uec.dongzong.my/file.pdf"))
        self.assertFalse(self.module.allowed_url("http://uec.dongzong.my/file.pdf"))
        self.assertFalse(self.module.allowed_url("https://dongzong.my.evil.example/file.pdf"))

    def test_discovers_embedded_pdf_viewer_url(self):
        page = '<div data-pdf="https:\\/\\/uec.dongzong.my\\/wp-content\\/uploads\\/J01.pdf"></div>'
        result = self.module.discover_documents("https://uec.dongzong.my/?p=315", page)
        self.assertEqual(result[0]["url"], "https://uec.dongzong.my/wp-content/uploads/J01.pdf")

    def test_discovers_subject_pages_for_selected_level(self):
        page = """
        <a href="/?p=113">高中统考考生人数</a>
        <a href="/?p=315">初中华文</a>
        <a href="/?cat=8">初中考试纲要/评量规格</a>
        <a href="/?p=369">高中会计学</a>
        <a href="/?cat=7">高中考试纲要/评量规格</a>
        <a href="/?page_id=62">初中历史作业报告</a>
        """
        result = self.module.discover_subject_pages("https://uec.dongzong.my/", page, "junior")
        self.assertEqual(result, [{"url": "https://uec.dongzong.my/?p=315", "label": "初中华文"}])

    def test_blocks_redirect_to_non_official_host(self):
        handler = self.module.OfficialOnlyRedirectHandler()
        request = Request("https://uec.dongzong.my/start")
        with self.assertRaisesRegex(ValueError, "Blocked redirect"):
            handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/file.pdf")

    def test_duplicate_basenames_get_distinct_destinations(self):
        with tempfile.TemporaryDirectory() as directory:
            used = {}
            first = self.module.unique_destination(
                Path(directory), "https://uec.dongzong.my/a/syllabus.pdf", "A", 1, used
            )
            second = self.module.unique_destination(
                Path(directory), "https://uec.dongzong.my/b/syllabus.pdf", "B", 2, used
            )
            self.assertNotEqual(first, second)
            self.assertEqual(first.name, "syllabus.pdf")
            self.assertRegex(second.name, r"^syllabus-[0-9a-f]{8}\.pdf$")

    def test_partial_index_failure_returns_error(self):
        config = {
            "publisher": "Dong Zong",
            "syllabus_indexes": [
                {"level": "junior", "title": "Junior", "url": "https://uec.dongzong.my/junior", "expected_subject_count": 1},
                {"level": "senior", "title": "Senior", "url": "https://uec.dongzong.my/senior", "expected_subject_count": 1},
            ],
        }
        senior_index = b'<a href="/?p=1">\xe9\xab\x98\xe4\xb8\xad\xe5\x8e\x86\xe5\x8f\xb2</a><a href="/?cat=7">category</a>'
        senior_subject = b'<div data-pdf="https://uec.dongzong.my/files/S08.pdf"></div>'

        def fake_fetch(url, max_bytes=None):
            if url.endswith("/junior"):
                raise OSError("offline")
            if url.endswith("/senior"):
                return senior_index
            return senior_subject

        args = argparse.Namespace(level="all", cache_dir=Path("unused"), sources=Path("unused"), list_only=True)
        with (
            patch.object(self.module, "parse_args", return_value=args),
            patch.object(self.module, "load_sources", return_value=config),
            patch.object(self.module, "fetch_bytes", side_effect=fake_fetch),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(self.module.main(), 2)

    def test_rejects_html_masquerading_as_pdf(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.module.validate_document_payload("https://uec.dongzong.my/file.pdf", b"<html>error</html>")
        self.module.validate_document_payload("https://uec.dongzong.my/file.pdf", b"%PDF-1.7")

    def test_fetch_retries_transient_connection_error(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.geturl.return_value = "https://uec.dongzong.my/file.pdf"
        response.headers = {}
        response.read.return_value = b"%PDF-1.7"
        with (
            patch.object(self.module.OPENER, "open", side_effect=[ConnectionResetError("reset"), response]) as opened,
            patch.object(self.module.time, "sleep") as slept,
        ):
            payload = self.module.fetch_bytes("https://uec.dongzong.my/file.pdf")
        self.assertEqual(payload, b"%PDF-1.7")
        self.assertEqual(opened.call_count, 2)
        slept.assert_called_once_with(0.5)


class InspectDocxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_script("inspect_docx.py")

    def test_inventory_preserves_body_order_and_ancillary_parts(self):
        document = """<?xml version="1.0" encoding="UTF-8"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
          xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
          <w:body>
            <w:p><w:r><w:t>正文</w:t></w:r><w:drawing><wp:docPr id="1" name="图一" descr="说明"/><a:blip r:embed="rId5"/></w:drawing></w:p>
            <w:tbl><w:tr><w:tc><w:p><w:r><w:t>A</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>B</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
          </w:body>
        </w:document>"""
        relationships = """<?xml version="1.0" encoding="UTF-8"?>
        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
          <Relationship Id="rId5" Target="media/image1.png" Type="image"/>
        </Relationships>"""
        header = """<?xml version="1.0" encoding="UTF-8"?>
        <w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>页眉</w:t></w:r></w:p></w:hdr>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document)
                archive.writestr("word/_rels/document.xml.rels", relationships)
                archive.writestr("word/header1.xml", header)
                archive.writestr("word/media/image1.png", b"png")
            result = self.module.inventory(path)
        self.assertEqual([item["type"] for item in result["items_in_document_order"]], ["paragraph", "table"])
        self.assertEqual(result["items_in_document_order"][1]["rows"], [["A", "B"]])
        self.assertEqual(result["main_body_pictures"][0]["target"], "media/image1.png")
        self.assertEqual(result["main_body_pictures"][0]["description"], "说明")
        self.assertEqual(result["ancillary_parts"][0]["text"], "页眉")


class PackageTests(unittest.TestCase):
    def test_relative_markdown_links_exist(self):
        missing = []
        pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        for markdown in ROOT.rglob("*.md"):
            for target in pattern.findall(markdown.read_text(encoding="utf-8")):
                clean = target.strip("<>").split("#", 1)[0]
                if not clean or clean.startswith(("http://", "https://", "mailto:")):
                    continue
                if not (markdown.parent / clean).resolve().exists():
                    missing.append(f"{markdown.relative_to(ROOT)} -> {clean}")
        self.assertEqual(missing, [])

    def test_cross_subject_eval_catalog_is_present(self):
        data = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        ids = {item["id"] for item in data["evals"]}
        self.assertTrue({
            "history-table-map",
            "science-experiment",
            "mathematics-formula",
            "language-notebooklm-privacy",
            "no-syllabus-access",
            "word-concise-template",
        }.issubset(ids))


if __name__ == "__main__":
    unittest.main()
