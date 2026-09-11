from pathlib import Path
import importlib.util
import unittest


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


if __name__ == "__main__":
    unittest.main()
