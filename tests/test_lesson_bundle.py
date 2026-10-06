"""Behavior checks for incomplete sources, page drift and false PPTX files."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bundle_check", ROOT / "scripts/check_lesson_bundle.py")
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class LessonBundleTests(unittest.TestCase):
    def setUp(self):
        # Keep fixtures in memory-backed test scope; no user lesson data is used.
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.state = {
            "schema_version": 1, "curriculum_route": "custom", "slide_route": "notebooklm",
            "sources": {"material": "material.txt", "lesson_plan": "plan.md", "outline": "outline.md", "teacher_notes": "notes.md"},
            "page_ids": ["P01", "P02"],
            "steps": {"slides": "awaiting_auth", "qa": "pending"}, "outputs": {},
        }
        for filename, text in {
            "material.txt": "Author-created fraction source.",
            "plan.md": "Lesson: thirty minutes.",
            "outline.md": "| P01 | First page |\n| P02 | Second page |",
            "notes.md": "## P01 First page\nExplain.\n## P02 Second page\nCheck.",
        }.items():
            (self.folder / filename).write_text(text, encoding="utf-8")

    def run_check(self):
        (self.folder / "task-state.json").write_text(json.dumps(self.state), encoding="utf-8")
        return bundle.validate_bundle(self.folder)

    def failed_labels(self, result):
        return [item["check"] for item in result["checks"] if not item["passed"]]

    def test_complete_local_sources_pass_without_claiming_generated_slides(self):
        result = self.run_check()
        self.assertTrue(result["ok"])
        self.assertTrue(any("not a completed" in warning for warning in result["warnings"]))

    def test_missing_material_role_blocks_notebooklm_bundle(self):
        self.state["sources"].pop("material")
        self.assertFalse(self.run_check()["ok"])

    def test_empty_source_is_not_treated_as_ready(self):
        (self.folder / "material.txt").write_text("", encoding="utf-8")
        self.assertFalse(self.run_check()["ok"])

    def test_same_file_cannot_impersonate_four_roles(self):
        self.state["sources"] = dict.fromkeys(self.state["sources"], "material.txt")
        self.assertIn("four roles use four distinct files", self.failed_labels(self.run_check()))

    def test_reordered_notes_fail_page_correspondence(self):
        (self.folder / "notes.md").write_text("## P02 Second\n## P01 First", encoding="utf-8")
        self.assertFalse(self.run_check()["ok"])

    def test_duplicate_planned_page_fails(self):
        self.state["page_ids"] = ["P01", "P01"]
        self.assertFalse(self.run_check()["ok"])

    def test_plain_lesson_does_not_require_notebooklm_or_slide_sources(self):
        self.state["slide_route"] = None
        self.state["page_ids"] = []
        self.state["sources"] = {"material": "material.txt", "lesson_plan": "plan.md"}
        self.state["steps"] = {"lesson_plan": "complete"}
        self.assertTrue(self.run_check()["ok"])

    def test_completed_slides_without_file_fail(self):
        self.state["steps"]["slides"] = "complete"
        self.assertFalse(self.run_check()["ok"])

    def test_pdf_renamed_pptx_fails(self):
        (self.folder / "slides.pptx").write_bytes(b"%PDF-1.7\nnot a PowerPoint file")
        self.state["outputs"]["slides"] = "slides.pptx"
        self.assertFalse(self.run_check()["ok"])

    def test_editable_missing_lesson_plan_fails(self):
        self.state["slide_route"] = "editable"
        self.state["sources"].pop("lesson_plan")
        self.assertFalse(self.run_check()["ok"])

    def test_preflight_is_not_complete_delivery(self):
        self.run_check()
        self.assertFalse(bundle.validate_bundle(self.folder, require_complete=True)["ok"])

    def prepare_complete(self):
        self.make_pptx()
        self.state["steps"] = dict.fromkeys(("lesson_plan", "outline", "teacher_notes", "slides", "qa"), "complete")
        (self.folder / "qa.md").write_text("Recorded visual review evidence.", encoding="utf-8")
        self.state["outputs"]["qa_report"] = "qa.md"
        sync = {"pages": [{"id": pid, "slide_number": i, "actual_title": pid, "outline_ref": pid, "notes_ref": pid, "lesson_plan_ref": "teaching activity", "status": "matched"} for i, pid in enumerate(self.state["page_ids"], 1)], "files": {}}
        for role, filename in {**self.state["sources"], "slides": "slides.pptx"}.items():
            if role == "material":
                continue
            sync["files"][role] = {"path": filename, "sha256": hashlib.sha256((self.folder / filename).read_bytes()).hexdigest()}
        (self.folder / "sync.json").write_text(json.dumps(sync), encoding="utf-8")
        self.state["outputs"]["page_sync"] = "sync.json"


    def test_complete_delivery_passes_structural_checks(self):
        self.prepare_complete()
        self.run_check()
        self.assertTrue(bundle.validate_bundle(self.folder, require_complete=True)["ok"])

    def test_pdf_cannot_complete_pptx_delivery(self):
        self.prepare_complete()
        (self.folder / "slides.pdf").write_bytes(b"%PDF-1.7")
        self.state["outputs"]["slides"] = "slides.pdf"
        self.run_check()
        self.assertFalse(bundle.validate_bundle(self.folder, require_complete=True)["ok"])

    def test_missing_qa_report_blocks_complete_delivery(self):
        self.prepare_complete()
        self.state["outputs"].pop("qa_report")
        self.run_check()
        self.assertFalse(bundle.validate_bundle(self.folder, require_complete=True)["ok"])


    def test_changed_notes_invalidate_sync(self):
        self.prepare_complete()
        with (self.folder / "notes.md").open("a", encoding="utf-8") as stream:
            stream.write("\nChanged content.")
        self.run_check()
        self.assertFalse(bundle.validate_bundle(self.folder, require_complete=True)["ok"])

    def test_missing_page_sync_blocks_complete_delivery(self):
        self.prepare_complete()
        self.state["outputs"].pop("page_sync")
        self.run_check()
        self.assertFalse(bundle.validate_bundle(self.folder, require_complete=True)["ok"])

    def test_wrong_slide_order_blocks_complete_delivery(self):
        self.prepare_complete()
        path = self.folder / "sync.json"
        sync = json.loads(path.read_text())
        sync["pages"][0]["slide_number"] = 2
        path.write_text(json.dumps(sync))
        self.run_check()
        self.assertFalse(bundle.validate_bundle(self.folder, require_complete=True)["ok"])

    def make_pptx(self, pages=2, missing_slide=False):
        with zipfile.ZipFile(self.folder / "slides.pptx", "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types/>")
            ids = "".join(f'<p:sldId id="{256+i}" r:id="rId{i}"/>' for i in range(1, pages+1))
            archive.writestr("ppt/presentation.xml", f'<p:presentation xmlns:p="{bundle.P_NS}" xmlns:r="{bundle.R_NS}"><p:sldIdLst>{ids}</p:sldIdLst></p:presentation>')
            rels = "".join(f'<Relationship Id="rId{i}" Target="slides/slide{i}.xml"/>' for i in range(1, pages+1))
            archive.writestr("ppt/_rels/presentation.xml.rels", f'<Relationships>{rels}</Relationships>')
            for i in range(1, pages+1):
                if missing_slide and i == pages:
                    continue
                archive.writestr(f"ppt/slides/slide{i}.xml", f'<p:sld xmlns:p="{bundle.P_NS}"/>')
        self.state["outputs"]["slides"] = "slides.pptx"
        self.state["steps"]["slides"] = "complete"

    def test_linked_pptx_page_count_is_checked(self):
        self.make_pptx()
        self.assertTrue(self.run_check()["ok"])

    def test_generated_extra_page_is_reported(self):
        self.make_pptx(pages=3)
        self.assertFalse(self.run_check()["ok"])

    def test_missing_linked_slide_is_reported(self):
        self.make_pptx(missing_slide=True)
        self.assertFalse(self.run_check()["ok"])

    def test_invalid_json_fails_without_traceback(self):
        (self.folder / "task-state.json").write_text("{", encoding="utf-8")
        self.assertFalse(bundle.validate_bundle(self.folder)["ok"])

    def test_invalid_field_type_is_reported(self):
        self.state["curriculum_route"] = ["custom"]
        self.state["slide_route"] = {"notebooklm": True}
        self.assertFalse(self.run_check()["ok"])

    def test_cli_json_and_exit_code_report_failure(self):
        self.state["sources"].pop("outline")
        self.run_check()
        output = io.StringIO()
        with patch("sys.argv", ["check", str(self.folder), "--json"]), contextlib.redirect_stdout(output):
            self.assertEqual(bundle.main(), 1)
        self.assertFalse(json.loads(output.getvalue())["ok"])


if __name__ == "__main__":
    unittest.main()
