#!/usr/bin/env python3
"""Write one short relaxing text to the entry file."""

# The entry text is fixed: one short piece, written exactly as-is.
import os
import sys

TEXT = "The light from the oldest stars left home before there were eyes to see it. It crossed the dark without hurrying, and it is still arriving, one photon at a time. You are reading it now."

DEFAULT_TARGET = "/output/entry.txt"


def pick_target(argv):
    if len(argv) > 1:
        return argv[1]
    env_target = os.environ.get("ENTRY_OUTPUT")
    if env_target:
        return env_target
    return DEFAULT_TARGET


def main(argv):
    target = pick_target(argv)
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as handle:
        handle.write(TEXT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
