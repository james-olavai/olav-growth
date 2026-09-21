#!/usr/bin/env python3
"""Unified Configuration & Environment Loader for Marketing OS."""

import json
import os
import sys
from pathlib import Path


def find_workspace_root() -> Path:
    """Walk up parent hierarchy to find project root (containing config.json or content/)."""
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config.json").is_file() or (p / "content").is_dir():
            return p
    return Path.cwd()


def load_env(override: bool = False):
    """Load variables from .env into os.environ."""
    root = find_workspace_root()
    env_file = root / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if override or k not in os.environ:
                os.environ[k] = v


def load_config() -> dict:
    """Load config.json merged with environment variables."""
    load_env()
    root = find_workspace_root()
    cfg_file = root / "config.json"
    cfg = {}
    if cfg_file.is_file():
        try:
            cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARNING] Failed to parse config.json: {e}", file=sys.stderr)
    return cfg


if __name__ == "__main__":
    c = load_config()
    print("Project Root:", find_workspace_root())
    print("Config JSON loaded:", json.dumps(c, indent=2, ensure_ascii=False))
