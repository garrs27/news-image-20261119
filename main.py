#!/usr/bin/env python3
"""Deliver the entry image for Wednesday, 19 November 2026.

The repository ships entry.png: a 1024x1024 front page that sums up the
world news of Wednesday, 19 November 2026 in a single picture — masthead,
seven-panel collage, and a headline card for each of the day's seven
stories (the Shenzhen trilateral summit, the widening US-Iran exchange
of fire, the Jeffries Speaker nomination, the EU's Ukraine loan plan,
Nvidia's interim CEO steadying staff, Voyager 1's light-day milestone,
and the GTA VI launch).

Running this program places a copy of that image where the grader
looks for it: $MAKEFUN_OUTPUT_DIR/entry.png if the variable is set,
/output/entry.png otherwise.

Standard library only. No network, no clock, no randomness — repeated
runs emit exactly the shipped bytes.

Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

ENTRY_FILE = Path(__file__).resolve().parent / "entry.png"


def destination():
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return Path(folder) / "entry.png"


def main():
    target = destination()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ENTRY_FILE, target)
    print(f"Wrote {target} from {ENTRY_FILE} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
