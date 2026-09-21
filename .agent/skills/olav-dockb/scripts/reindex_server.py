#!/usr/bin/env python3
"""Optional HTTP trigger for a docs-kb reindex — for deployments where nothing
runs `extract_docs.py`/`ocr_extract.py`/`add_frontmatter.py` on a schedule and
you want a UI button or webhook to kick off a run instead of a human running
the scripts by hand.

This file sits in the docs-kb scripts directory and shells out to three of its
neighbours, but it is not an engine script itself: it's a thin HTTP wrapper
around the same pipeline the "Quick start" in README.md runs manually, meant
to be started as a long-lived background process (e.g. from your own
container entrypoint or a systemd unit) and called at `POST /reindex` by
whatever UI/automation you point at it. Standard library only — one endpoint
plus a fixed subprocess pipeline does not need a web framework.

Keep it dependency-free: uvicorn/flask would be a new dependency for a single
endpoint; `http.server` already covers "one POST in, three exit codes out".
Everything below is deliberately synchronous — the caller applies its own
timeout, this server only refuses concurrent runs (see the in-process lock).

Usage:  python3 reindex_server.py        # listens on 0.0.0.0:8791
"""
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

# The pipeline scripts are resolved next to this file, not relative to
# whatever directory this server was launched from: callers may start it by
# an absolute path, and the subprocesses get `cwd=SCRIPTS_DIR` so `import
# classify` etc. in the engine scripts keep working exactly as they do when
# run by hand.
SCRIPTS_DIR = Path(__file__).resolve().parent

HOST = "0.0.0.0"
PORT = 8791

# Order matters (and is the same as docs-kb README/SKILL.md "quick start"):
#   extract_docs.py        office/spreadsheet -> .md/.csv companions
#   ocr_extract.py         scanned PDFs/images -> .md companions
#   add_frontmatter.py     classify every .md the first two just wrote
# DOCS_KB_ROOT is not passed explicitly: it must already be set in this
# process's own environment (see README.md), and subprocess.run inherits the
# parent environment by default.
PIPELINE = (
    ("extract_output", ("extract_docs.py",)),
    ("ocr_output", ("ocr_extract.py",)),
    ("frontmatter_output", ("add_frontmatter.py", "--apply")),
)


def _run_step(argv):
    """Run one engine script; returns its exit code and captured output.

    `sys.executable` (not the string "python") because the image base is
    python:3.12-slim and a bare `python` alias is not guaranteed. Explicit
    UTF-8 decoding because the engine scripts reconfigure their stdout to
    utf-8 while a slim image's locale may not be.
    """
    proc = subprocess.run(
        [sys.executable, *argv],
        cwd=SCRIPTS_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def run_pipeline():
    """Run all three steps in order and collect every exit code.

    A non-zero exit does not abort the pipeline: companions produced by the
    earlier steps still deserve to be classified, and the caller gets each
    returncode (not just concatenated text) so it can tell "this step really
    failed" from "this step printed nothing".
    """
    return {key: _run_step(argv) for key, argv in PIPELINE}


class ReindexServer(ThreadingHTTPServer):
    """Threaded so a second request can be answered (409) while one runs."""

    daemon_threads = True

    def __init__(self, server_address, handler_class):
        super().__init__(server_address, handler_class)
        self.reindex_lock = threading.Lock()


class ReindexHandler(BaseHTTPRequestHandler):
    server_version = "docs-kb-reindex/1.0"

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self):
        # Any request that is not `POST /reindex` gets 404 and does not touch
        # the pipeline (and never takes the server process down).
        self._send_json(404, {"ok": False, "reason": "not found"})

    do_GET = _not_found
    do_PUT = _not_found
    do_DELETE = _not_found
    do_PATCH = _not_found
    do_OPTIONS = _not_found

    def do_HEAD(self):
        # Same 404, but HEAD responses carry no body.
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        if urlsplit(self.path).path != "/reindex":
            self._not_found()
            return
        lock = self.server.reindex_lock
        if not lock.acquire(blocking=False):
            # No queueing: a second run would write the same files concurrently
            # (add_frontmatter.py --apply and the OCR pass must not race on
            # one corpus — see that script's own red team).
            self._send_json(409, {"ok": False, "reason": "reindex already running"})
            return
        try:
            outputs = run_pipeline()
        except Exception as err:  # subprocess itself failed to start (missing cwd, permissions…)
            # The HTTP server process must survive a broken step; report 500 and
            # let the next request try again with a fresh lock.
            self._send_json(500, {"ok": False, "reason": str(err)})
        else:
            self._send_json(200, {"ok": True, **outputs})
        finally:
            lock.release()


def create_server(port=PORT, host=HOST):
    return ReindexServer((host, port), ReindexHandler)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Optional HTTP trigger daemon for docs-kb reindexing pipeline")
    parser.add_argument("--host", default=HOST, help=f"Host to bind (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port to bind (default: {PORT})")
    args = parser.parse_args()

    server = create_server(port=args.port, host=args.host)
    print(f"[docs-kb] reindex server listening on {args.host}:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
