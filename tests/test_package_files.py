"""Verify packaging includes new work and detects tracked runtime caches."""
import subprocess
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_package.py"
SPEC = importlib.util.spec_from_file_location("package_validator", SCRIPT)
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)
package_files = PACKAGE.package_files


class PackageFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content="example"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, check=True)

    def names(self):
        return {path.relative_to(self.root).as_posix() for path in package_files(self.root)}

    def test_untracked_documents_included(self):
        self.git("init")
        self.write("new lesson.md")
        self.assertIn("new lesson.md", self.names())

    def test_ignored_local_cache_excluded(self):
        self.git("init")
        self.write(".gitignore", "__pycache__/\n")
        self.write("scripts/__pycache__/local.pyc")
        self.assertNotIn("scripts/__pycache__/local.pyc", self.names())

    def test_tracked_cache_never_hidden_by_ignore(self):
        self.git("init")
        self.write(".gitignore", "__pycache__/\n")
        self.write("scripts/__pycache__/tracked.pyc")
        self.git("add", "--force", "scripts/__pycache__/tracked.pyc")
        self.assertIn("scripts/__pycache__/tracked.pyc", self.names())

    def test_source_archive_checks_cache_and_documents(self):
        self.write("README.md")
        self.write("scripts/__pycache__/unexpected.pyc")
        self.assertEqual(self.names(), {"README.md", "scripts/__pycache__/unexpected.pyc"})

    def test_git_failure_does_not_silently_skip_checks(self):
        (self.root / ".git").mkdir()
        with patch.object(PACKAGE.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "git")):
            with self.assertRaises(subprocess.CalledProcessError):
                package_files(self.root)


if __name__ == "__main__":
    unittest.main()
