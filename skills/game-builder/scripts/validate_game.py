#!/usr/bin/env python3
"""Validate a generated browser game directory and its local resources."""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REMOTE_RE = re.compile(r"(?:https?:)?//", re.I)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^)'\"]+)", re.I)
REQUIRED = (
    "index.html",
    "README.md",
    "score-schema.json",
    "resources/assets-manifest.json",
    "resources/css/app.css",
    "resources/js/app.js",
)


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value and name.lower() in {"src", "href", "poster"}:
                self.values.append(value)


def local_target(base: Path, reference: str) -> Path | None:
    if reference.startswith(("#", "data:", "mailto:", "javascript:")):
        return None
    parts = urlsplit(reference)
    if parts.scheme or parts.netloc:
        return None
    return (base / unquote(parts.path)).resolve()


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append(f"missing: {relative}")
    if errors:
        return errors

    index = (root / "index.html").read_text(encoding="utf-8")
    parser = References()
    parser.feed(index)
    if '<meta name="viewport"' not in index.lower():
        errors.append("index.html: viewport meta is required")
    if "<title" not in index.lower():
        errors.append("index.html: title is required")

    text_files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".html", ".css", ".js"}]
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        if REMOTE_RE.search(text):
            errors.append(f"{path.relative_to(root).as_posix()}: remote URL or protocol-relative resource found")
        references = CSS_URL_RE.findall(text) if path.suffix.lower() == ".css" else []
        if path.name == "index.html":
            references.extend(parser.values)
        for reference in references:
            target = local_target(path.parent, reference)
            if target is None:
                continue
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"{path.relative_to(root).as_posix()}: resource escapes game directory: {reference}")
                continue
            if not target.is_file():
                errors.append(f"{path.relative_to(root).as_posix()}: missing resource: {reference}")

    app_js = (root / "resources/js/app.js").read_text(encoding="utf-8")
    for marker, label in (("localStorage", "local ranking"), ("JSON.stringify", "JSON export"), ("JSON.parse", "JSON import")):
        if marker not in app_js:
            errors.append(f"resources/js/app.js: {label} marker not found")

    for relative in ("score-schema.json", "resources/assets-manifest.json"):
        try:
            json.loads((root / relative).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", type=Path, help="Generated game directory")
    args = parser.parse_args()
    if not args.game.is_dir():
        parser.error(f"directory not found: {args.game}")
    errors = validate(args.game)
    if errors:
        print(f"FAIL: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {args.game}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
