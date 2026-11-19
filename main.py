#!/usr/bin/env python3.13
"""Deliver the finished front-page image for the news-image-20261119 entry.

The artwork itself is baked ahead of time and committed to this repository
as ``entry.png``.  At run time there is nothing left to render: this module
simply ferries that file, untouched, into whichever directory the make.fun
runner points us at through the ``MAKEFUN_OUTPUT_DIR`` environment
variable (falling back to ``/output`` when the variable is absent).

Copying rather than re-encoding is deliberate.  A byte-for-byte transfer
guarantees the judges see exactly the pixels that were reviewed before
submission, with no compression artefacts, colour shifts or resizing
surprises introduced at the last moment.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Name of the committed artwork, sitting right beside this file.
ARTWORK_NAME = "entry.png"

# Where the runner expects deliverables when it does not tell us otherwise.
FALLBACK_OUTPUT_DIR = "/output"

# Environment variable the harness uses to hand us an output directory.
OUTPUT_DIR_ENV_VAR = "MAKEFUN_OUTPUT_DIR"


def artwork_path() -> Path:
    """Return the absolute path of the artwork shipped with this entry."""
    return Path(__file__).resolve().parent / ARTWORK_NAME


def destination_path() -> Path:
    """Work out where the runner wants the artwork to end up."""
    requested = os.environ.get(OUTPUT_DIR_ENV_VAR, "").strip()
    base = Path(requested) if requested else Path(FALLBACK_OUTPUT_DIR)
    return base / ARTWORK_NAME


def deliver() -> Path:
    """Copy the artwork to the destination and return that path.

    Raises ``FileNotFoundError`` if the committed artwork is missing,
    which would mean the repository checkout is incomplete.
    """
    source = artwork_path()
    if not source.is_file():
        raise FileNotFoundError(f"committed artwork not found: {source}")

    target = destination_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

    # Paranoia worth having: a truncated copy would still "succeed" at
    # the shutil level on some filesystems, so confirm the sizes agree
    # before we claim delivery.
    if target.stat().st_size != source.stat().st_size:
        raise OSError(f"copy size mismatch: {source} -> {target}")
    return target


def main() -> int:
    """Console entry point: deliver the image and print a receipt line."""
    try:
        target = deliver()
    except OSError as exc:
        print(f"delivery failed: {exc}", file=sys.stderr)
        return 1

    size = target.stat().st_size
    print(f"delivered {ARTWORK_NAME}: {size} bytes -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
