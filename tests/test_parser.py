import json
from pathlib import Path
import subprocess
import sys
import unittest

from diff_review import parse_diff


ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_replacement_line_numbers(self):
        file = parse_diff((ROOT / "examples/hello.diff").read_text())[0]
        self.assertEqual((file["old_path"], file["new_path"]), ("hello.py", "hello.py"))
        lines = file["hunks"][0]["lines"]
        self.assertEqual(
            [(line["type"], line["old_line"], line["new_line"]) for line in lines],
            [("context", 1, 1), ("delete", 2, None), ("add", None, 2), ("add", None, 3)],
        )

    def test_new_and_deleted_files(self):
        files = parse_diff(
            "--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1 @@\n+hello\n"
            "--- a/old.txt\n+++ /dev/null\n@@ -1 +0,0 @@\n-goodbye\n"
        )
        self.assertIsNone(files[0]["old_path"])
        self.assertIsNone(files[1]["new_path"])
        self.assertEqual(files[1]["hunks"][0]["lines"][0]["old_line"], 1)

    def test_multiple_hunks_and_no_newline(self):
        file = parse_diff(
            "--- a/x\n+++ b/x\n@@ -1 +1 @@ first\n-old\n"
            "\\ No newline at end of file\n+new\n"
            "\\ No newline at end of file\n@@ -10 +10 @@\n same\n"
        )[0]
        self.assertEqual(len(file["hunks"]), 2)
        self.assertEqual(file["hunks"][0]["heading"], "first")
        self.assertTrue(all(line["no_newline"] for line in file["hunks"][0]["lines"]))
        self.assertEqual(file["hunks"][1]["lines"][0]["new_line"], 10)

    def test_empty_diff(self):
        self.assertEqual(parse_diff(""), [])

    def test_invalid_and_unsupported_input(self):
        for patch in (
            "not a patch",
            "--- a/x\n+++ b/x\n@@ -1,2 +1,2 @@\n same\n",
            "--- a/x\n+++ b/x\n@@ -0,0 +1 @@\n context\n",
            "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a\n+b\n+extra\n",
            "Binary files a/image.png and b/image.png differ",
            "@@@ -1,1 -1,1 +1,1 @@@",
            '--- "a/quoted\\tname"\n+++ b/x\n',
        ):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                parse_diff(patch)

    def test_cli_file_and_stdin(self):
        patch = ROOT / "examples/hello.diff"
        for args, stdin in (([str(patch)], None), ([], patch.read_text())):
            result = subprocess.run(
                [sys.executable, "-m", "diff_review"] + args,
                input=stdin, text=True, capture_output=True, cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)[0]["new_path"], "hello.py")

    def test_cli_invalid_input_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, "-m", "diff_review"], input="invalid", text=True,
            capture_output=True, cwd=ROOT,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("diff-review:", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
