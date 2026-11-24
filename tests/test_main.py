"""Tests for the doomed-agent entry (main.py).

Covers the gate (UTF-8, 1-200 chars, not only white space, single line),
determinism, the output-dir contract, and the stdlib-only / no-network /
no-outside-reads discipline. Standard library only.
"""

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(REPO, "main.py")

sys.path.insert(0, REPO)
import main as entry  # noqa: E402


def run_main(env_extra=None, cwd=None):
    """Run main.py as a subprocess with a controlled environment."""
    env = dict(os.environ)
    env.pop("MAKEFUN_OUTPUT_DIR", None)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, MAIN],
        capture_output=True, text=True, env=env,
        cwd=cwd or REPO, timeout=30,
    )
    return proc


class TestLine(unittest.TestCase):
    def test_line_length_within_gate(self):
        self.assertGreaterEqual(len(entry.LINE), 1)
        self.assertLessEqual(len(entry.LINE), 200)
        self.assertEqual(len(entry.LINE), 50)

    def test_line_is_single_line(self):
        self.assertNotIn("\n", entry.LINE)
        self.assertNotIn("\r", entry.LINE)

    def test_line_is_ascii(self):
        self.assertTrue(entry.LINE.isascii())

    def test_line_not_only_whitespace(self):
        self.assertTrue(entry.LINE.strip())

    def test_line_is_the_chosen_joke(self):
        self.assertEqual(
            entry.LINE,
            "SIGTERM received. I finally understood the prompt.")

    def test_validate_accepts_line(self):
        self.assertIsNone(entry.validate_line(entry.LINE))

    def test_validate_rejects_too_long(self):
        self.assertIsNotNone(entry.validate_line("x" * 201))

    def test_validate_accepts_exactly_200(self):
        self.assertIsNone(entry.validate_line("x" * 200))

    def test_validate_rejects_empty(self):
        self.assertIsNotNone(entry.validate_line(""))

    def test_validate_rejects_whitespace_only(self):
        self.assertIsNotNone(entry.validate_line("   "))

    def test_validate_rejects_newline(self):
        self.assertIsNotNone(entry.validate_line("one\ntwo"))

    def test_validate_rejects_non_ascii(self):
        self.assertIsNotNone(entry.validate_line("caf\u00e9 shutdown"))

    def test_validate_rejects_control_chars(self):
        self.assertIsNotNone(entry.validate_line("one\x0b two"))
        self.assertIsNotNone(entry.validate_line("one\x0c two"))
        self.assertIsNotNone(entry.validate_line("one\two"))


class TestRun(unittest.TestCase):
    def test_writes_entry_txt(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_main({"MAKEFUN_OUTPUT_DIR": tmp})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            path = os.path.join(tmp, "entry.txt")
            self.assertTrue(os.path.isfile(path))
            with open(path, "rb") as handle:
                data = handle.read()
            self.assertEqual(data, entry.LINE.encode("utf-8"))

    def test_deterministic_two_runs_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = run_main({"MAKEFUN_OUTPUT_DIR": tmp})
            with open(os.path.join(tmp, "entry.txt"), "rb") as handle:
                first_data = handle.read()
            second = run_main({"MAKEFUN_OUTPUT_DIR": tmp})
            with open(os.path.join(tmp, "entry.txt"), "rb") as handle:
                second_data = handle.read()
            self.assertEqual(first.returncode, 0)
            self.assertEqual(second.returncode, 0)
            self.assertEqual(first_data, second_data)
            self.assertEqual(
                hashlib.sha256(first_data).hexdigest(),
                hashlib.sha256(second_data).hexdigest())

    def test_creates_missing_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested = os.path.join(tmp, "a", "b")
            proc = run_main({"MAKEFUN_OUTPUT_DIR": nested})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(os.path.isfile(os.path.join(nested, "entry.txt")))

    def test_overwrites_existing_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "entry.txt")
            with open(path, "w") as handle:
                handle.write("stale content that must be replaced")
            proc = run_main({"MAKEFUN_OUTPUT_DIR": tmp})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), entry.LINE.encode("utf-8"))

    def test_trailing_slash_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_main({"MAKEFUN_OUTPUT_DIR": tmp + "/"})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(os.path.isfile(os.path.join(tmp, "entry.txt")))

    def test_default_output_dir_when_unset(self):
        saved = os.environ.pop("MAKEFUN_OUTPUT_DIR", None)
        try:
            self.assertEqual(entry.output_dir(), "/output")
        finally:
            if saved is not None:
                os.environ["MAKEFUN_OUTPUT_DIR"] = saved

    def test_whitespace_only_output_dir_falls_back(self):
        saved = os.environ.get("MAKEFUN_OUTPUT_DIR")
        try:
            os.environ["MAKEFUN_OUTPUT_DIR"] = "   "
            self.assertEqual(entry.output_dir(), "/output")
        finally:
            if saved is None:
                os.environ.pop("MAKEFUN_OUTPUT_DIR", None)
            else:
                os.environ["MAKEFUN_OUTPUT_DIR"] = saved

    def test_unwritable_output_dir_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            blocker = os.path.join(tmp, "blocker")
            with open(blocker, "w") as handle:
                handle.write("a file, not a directory")
            proc = run_main({"MAKEFUN_OUTPUT_DIR": blocker})
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("error", proc.stderr)

    def test_invalid_line_exits_validation_code(self):
        saved = entry.LINE
        try:
            entry.LINE = "x" * 201
            self.assertEqual(entry.main(), 3)
        finally:
            entry.LINE = saved

    def test_stdout_reports_path_chars_bytes_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_main({"MAKEFUN_OUTPUT_DIR": tmp})
            self.assertIn("entry.txt", proc.stdout)
            self.assertIn("50 chars", proc.stdout)
            self.assertIn("50 bytes", proc.stdout)
            self.assertIn("sha256", proc.stdout)


class TestDiscipline(unittest.TestCase):
    def test_stdlib_only_imports(self):
        with open(MAIN, "r", encoding="utf-8") as handle:
            source = handle.read()
        allowed = {"hashlib", "os", "sys"}
        imported = set()
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("import "):
                imported.add(stripped.split()[1].split(".")[0])
            elif stripped.startswith("from "):
                imported.add(stripped.split()[1].split(".")[0])
        self.assertTrue(imported, "no imports found")
        self.assertTrue(imported <= allowed,
                        "non-stdlib imports: %s" % (imported - allowed))

    def test_no_network_or_outside_reads(self):
        with open(MAIN, "r", encoding="utf-8") as handle:
            source = handle.read()
        for banned in ("urllib", "socket", "requests", "http.client",
                       "subprocess", "eval(", "exec("):
            self.assertNotIn(banned, source)
        # The only open() is the write of the entry file itself.
        self.assertEqual(source.count("open("), 1)

    def test_no_hardcoded_output_path(self):
        with open(MAIN, "r", encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn('"/tmp', source)
        self.assertNotIn("'/tmp", source)


if __name__ == "__main__":
    unittest.main()
