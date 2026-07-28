#!/usr/bin/env python3
"""Run bundled deterministic tests."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(root / "tests"),
        "-p",
        "test_*.py",
    ]
    if args.verbose:
        command.append("-v")
    raise SystemExit(subprocess.call(command, cwd=root))


if __name__ == "__main__":
    main()
