#!/usr/bin/env python3
"""Red-team / self-check suite for reindex_server.py.

reindex_server.py is the HTTP shell some deployment calls to trigger a docs-kb
reindex. This suite drives a real ThreadingHTTPServer over real sockets
(http.client, no mocking of the server or its transport) and asserts the
orchestration behavior that belongs to *this* script: mutual exclusion, 404 on
anything else, continue-on-nonzero, and survival of a broken subprocess start.
The three engine scripts it calls already have their own red teams
(redteam_extract_docs.py, and ocr_extract.py/add_frontmatter.py's own
review), so this suite
deliberately does not run markitdown/tesseract: each test gets a throwaway
scripts directory containing a copy of reindex_server.py plus small stub files
carrying the three engine names. The stubs log their invocation order into
order.log and take their behavior (exit code, stdout/stderr, sleep) from
control.json.

Note on failure injection: renaming a stub does NOT make subprocess.run raise —
`sys.executable` still exists, and CPython prints "can't open file" and exits
with code 2 (a normal non-zero step, covered by the continue-on-nonzero test).
The way subprocess.run itself raises FileNotFoundError is a missing cwd, which
is what test_subprocess_start_failure_returns_500_and_server_survives uses.

Run (from this directory):
    python -m unittest redteam_reindex_server.py -v
"""
import http.client
import importlib.util
import json
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SERVER_SOURCE = SCRIPTS_DIR / "reindex_server.py"

# key (used in control.json / order.log) -> engine script filename
STEPS = {
    "extract": "extract_docs.py",
    "ocr": "ocr_extract.py",
    "frontmatter": "add_frontmatter.py",
}

STUB_TEMPLATE = '''\
"""Throwaway stand-in for {name}: behavior comes from control.json."""
import json
import sys
import time
from pathlib import Path

here = Path(__file__).resolve().parent
control_path = here / "control.json"
config = json.loads(control_path.read_text(encoding="utf-8")) if control_path.exists() else {{}}
step = config.get("{key}", {{}})

with (here / "order.log").open("a", encoding="utf-8") as fh:
    fh.write("{key}\\n")

sys.stdout.write(step.get("stdout", ""))
sys.stderr.write(step.get("stderr", ""))
time.sleep(float(step.get("sleep", 0)))
sys.exit(int(step.get("exit", 0)))
'''


class ReindexServerCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="rt-reindex-server-"))
        shutil.copyfile(SERVER_SOURCE, self.root / "reindex_server.py")
        for key, filename in STEPS.items():
            self.write_stub(key, filename)
        self.set_control({})

        # Import the copy (not the original) so SCRIPTS_DIR resolves to this
        # throwaway directory and the stubs are what actually gets run.
        spec = importlib.util.spec_from_file_location(
            "reindex_server_under_test", self.root / "reindex_server.py"
        )
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

        # port=0: let the OS pick a free port instead of hard-coding 8791, so
        # the suite can never collide with a real container/process.
        self.server = self.module.create_server(port=0, host="127.0.0.1")
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        shutil.rmtree(self.root, ignore_errors=True)

    def write_stub(self, key, filename):
        (self.root / filename).write_text(
            STUB_TEMPLATE.format(name=filename, key=key), encoding="utf-8"
        )

    def set_control(self, control):
        (self.root / "control.json").write_text(json.dumps(control), encoding="utf-8")

    def request(self, method, path, timeout=30):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=timeout)
        try:
            conn.request(method, path)
            response = conn.getresponse()
            return response.status, json.loads(response.read().decode("utf-8"))
        finally:
            conn.close()

    def step_log(self):
        log = self.root / "order.log"
        if not log.exists():
            return []
        return log.read_text(encoding="utf-8").split()

    def wait_for_step(self, key, timeout=10):
        deadline = time.monotonic() + timeout
        while key not in self.step_log():
            self.assertLess(time.monotonic(), deadline, f"step {key!r} never started")
            time.sleep(0.02)


class HappyPathTest(ReindexServerCase):
    def test_single_run_returns_200_with_three_outputs_in_order(self):
        self.set_control(
            {
                "extract": {"stdout": "extract: 2 succeeded\n"},
                "ocr": {"stdout": "ocr: 1 skipped\n"},
                "frontmatter": {"stdout": "frontmatter: 3 files\n"},
            }
        )

        status, body = self.request("POST", "/reindex")

        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        # Every step is reported with its returncode, not just its text: the
        # caller needs to be able to say "this step failed" without parsing
        # the engine scripts' human-readable summaries.
        self.assertEqual(
            body["extract_output"],
            {"returncode": 0, "stdout": "extract: 2 succeeded\n", "stderr": ""},
        )
        self.assertEqual(body["ocr_output"]["returncode"], 0)
        self.assertEqual(body["ocr_output"]["stdout"], "ocr: 1 skipped\n")
        self.assertEqual(body["frontmatter_output"]["returncode"], 0)
        self.assertEqual(body["frontmatter_output"]["stdout"], "frontmatter: 3 files\n")
        # Order is the point of the pipeline: extract -> ocr -> classify.
        self.assertEqual(self.step_log(), ["extract", "ocr", "frontmatter"])


class ConcurrencyTest(ReindexServerCase):
    def test_second_request_while_running_gets_409_then_lock_is_released(self):
        self.set_control({"extract": {"sleep": 0.8}})
        first = {}

        def run_first():
            first["status"], first["body"] = self.request("POST", "/reindex")

        worker = threading.Thread(target=run_first)
        worker.start()
        # Only fire the second request once the first is provably inside the
        # slow step, so the test isn't racing the server's own startup.
        self.wait_for_step("extract")

        status, body = self.request("POST", "/reindex")
        self.assertEqual(status, 409)
        self.assertEqual(body, {"ok": False, "reason": "reindex already running"})

        worker.join(timeout=30)
        self.assertFalse(worker.is_alive(), "first request never completed")
        self.assertEqual(first["status"], 200)
        self.assertTrue(first["body"]["ok"])

        # And the error-free path released the lock: a fresh run must work.
        self.set_control({})
        status, body = self.request("POST", "/reindex")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])


class ContinueOnNonzeroTest(ReindexServerCase):
    def test_nonzero_step_does_not_stop_the_pipeline(self):
        self.set_control({"extract": {"exit": 3, "stderr": "boom\n"}})

        status, body = self.request("POST", "/reindex")

        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["extract_output"]["returncode"], 3)
        self.assertEqual(body["extract_output"]["stderr"], "boom\n")
        # The other two still ran even though the first one failed.
        self.assertEqual(body["ocr_output"]["returncode"], 0)
        self.assertEqual(body["frontmatter_output"]["returncode"], 0)
        self.assertEqual(self.step_log(), ["extract", "ocr", "frontmatter"])

    def test_missing_script_is_a_nonzero_step_not_a_crash(self):
        # Regression pin for the note at the top of this file: deleting a stub
        # yields exit code 2 from CPython ("can't open file"), not an exception
        # — the pipeline must keep going and still answer 200.
        (self.root / "ocr_extract.py").unlink()

        status, body = self.request("POST", "/reindex")

        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertNotEqual(body["ocr_output"]["returncode"], 0)
        self.assertIn("can't open file", body["ocr_output"]["stderr"])
        self.assertEqual(body["frontmatter_output"]["returncode"], 0)
        self.assertEqual(self.step_log(), ["extract", "frontmatter"])


class SubprocessFailureTest(ReindexServerCase):
    def test_subprocess_start_failure_returns_500_and_server_survives(self):
        # subprocess.run with a cwd that no longer exists raises FileNotFoundError.
        # (Renaming a script does not: see the docstring.) Simulate the scripts
        # directory itself vanishing under a running server.
        moved = self.root.with_name(self.root.name + "-moved")
        self.root.rename(moved)
        try:
            status, body = self.request("POST", "/reindex")
        finally:
            moved.rename(self.root)

        self.assertEqual(status, 500)
        self.assertFalse(body["ok"])
        self.assertIn("No such file or directory", body["reason"])

        # The process is still alive and the lock was released on the error path.
        status, body = self.request("POST", "/reindex")
        self.assertEqual(status, 200, body)
        self.assertTrue(body["ok"])
        self.assertEqual(self.step_log(), ["extract", "ocr", "frontmatter"])


class WrongRequestTest(ReindexServerCase):
    def test_wrong_method_or_path_gets_404_without_running_the_pipeline(self):
        for method, path in (("GET", "/reindex"), ("POST", "/wrong-path"), ("GET", "/")):
            status, body = self.request(method, path)
            self.assertEqual(status, 404, f"{method} {path}")
            self.assertEqual(body, {"ok": False, "reason": "not found"})
        self.assertEqual(self.step_log(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
