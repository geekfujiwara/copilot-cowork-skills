#!/usr/bin/env python3
"""Validate basic OOXML and media integrity of a PowerPoint file."""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

SLIDE_RE = re.compile(r"^ppt/slides/slide\d+\.xml$")
PLACEHOLDER_RE = re.compile(rb"\{\{[^{}]+\}\}|\b(?:lorem|xxxx)\b", re.I)
MAGIC = {
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".gif": b"GIF8",
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"file not found: {path}"]
    if path.read_bytes()[:4] != b"PK\x03\x04":
        return ["file is not an OOXML ZIP package"]

    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                errors.append(f"corrupt ZIP member: {bad}")
            names = archive.namelist()
            slides = sorted(name for name in names if SLIDE_RE.match(name))
            if not slides:
                errors.append("no slide XML found")
            if "[Content_Types].xml" not in names or "ppt/presentation.xml" not in names:
                errors.append("required OOXML parts are missing")

            for name in names:
                lower = name.lower()
                suffix = Path(lower).suffix
                if lower.startswith("ppt/media/") and suffix == ".svg":
                    errors.append(f"SVG media requires compatibility review: {name}")
                expected = MAGIC.get(suffix)
                if expected and lower.startswith("ppt/media/"):
                    if not archive.read(name).startswith(expected):
                        errors.append(f"media content does not match extension: {name}")

            searchable = b"\n".join(
                archive.read(name)
                for name in names
                if name.endswith((".xml", ".rels"))
            )
            if PLACEHOLDER_RE.search(searchable):
                errors.append("unresolved placeholder text found in OOXML")
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        errors.append(f"cannot read PPTX: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()
    errors = validate(args.pptx)
    if errors:
        print(f"FAIL: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {args.pptx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
