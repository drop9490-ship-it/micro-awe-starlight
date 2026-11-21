#!/usr/bin/env python3
"""Local gate for the micro awe entry.

Runs main.py twice into temp files, checks the two outputs are
byte-identical, validates the output (UTF-8, 1-280 code points,
not blank), and scans main.py for forbidden tokens.
"""

import hashlib
import os
import subprocess
import sys
import tempfile

FORBIDDEN = [
    "urllib",
    "requests",
    "socket",
    "http.client",
    "openai",
    "random",
    "datetime",
]


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    main_path = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    failures = []

    with open(main_path, "r", encoding="utf-8") as handle:
        source = handle.read()
    for token in FORBIDDEN:
        if token in source:
            failures.append("forbidden token in main.py: " + token)
    if failures:
        print("FAIL: " + "; ".join(failures))
    else:
        print("PASS: no forbidden tokens in main.py")

    tmpdir = tempfile.mkdtemp(prefix="awe-check-")
    first = os.path.join(tmpdir, "first.txt")
    second = os.path.join(tmpdir, "second.txt")

    for label, target in (("first", first), ("second", second)):
        result = subprocess.run(
            [sys.executable, main_path, target],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append("main.py " + label + " run failed: " + result.stderr.strip())
    if not failures:
        print("PASS: main.py runs twice without error")

    if os.path.exists(first) and os.path.exists(second):
        if digest(first) == digest(second):
            print("PASS: two runs are byte-identical")
        else:
            failures.append("two runs differ")

    if os.path.exists(first):
        with open(first, "rb") as handle:
            raw = handle.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            failures.append("output is not valid UTF-8")
            text = ""
        if text:
            if 1 <= len(text) <= 280:
                print("PASS: output is %d code points (1-280)" % len(text))
            else:
                failures.append("output length %d outside 1-280" % len(text))
            if text.strip():
                print("PASS: output is not blank")
            else:
                failures.append("output is blank")
            if raw.endswith(b"\n"):
                failures.append("output has a trailing newline")
            else:
                print("PASS: no trailing newline")

    if failures:
        for item in failures:
            print("FAIL: " + item)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
