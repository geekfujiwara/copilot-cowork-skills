import shutil
import tempfile
import unittest
from pathlib import Path

from audit_skill import check_assets


class ReviewedFontTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "video-editor"
        self.fonts = self.root / "assets" / "fonts"
        source = Path(__file__).resolve().parents[2] / "video-editor" / "assets" / "fonts"
        shutil.copytree(source, self.fonts)

    def status(self):
        return check_assets(str(self.root))[0]["status"]

    def test_reviewed_font_and_notice_pass(self):
        self.assertEqual(self.status(), "PASS")

    def test_changed_font_fails(self):
        (self.fonts / "NotoSansJP-VariableFont_wght.ttf").write_bytes(b"changed")
        self.assertEqual(self.status(), "FAIL")

    def test_missing_notice_fails(self):
        (self.fonts / "OFL.txt").unlink()
        self.assertEqual(self.status(), "FAIL")

    def test_changed_notice_fails(self):
        (self.fonts / "OFL.txt").write_text("changed", encoding="utf-8")
        self.assertEqual(self.status(), "FAIL")

    def test_other_font_fails(self):
        (self.fonts / "unreviewed.ttf").write_bytes(b"unreviewed")
        self.assertEqual(self.status(), "FAIL")

    def test_other_skill_fails(self):
        renamed = self.root.with_name("other-skill")
        self.root.rename(renamed)
        self.assertEqual(check_assets(str(renamed))[0]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
