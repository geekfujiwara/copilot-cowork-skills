#!/usr/bin/env python3
"""Download or validate planned MS Icons files in a local working folder."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

SVG_UNSAFE_RE = re.compile(
    rb"<(?:script|foreignObject)\b|\bon\w+\s*=|(?:href|src)\s*=\s*[\"'](?:https?:|data:|javascript:)",
    re.I,
)
MAGIC = {"png": b"\x89PNG\r\n\x1a\n"}


def _https_host(value: str, host: str, path_prefix: str = "") -> bool:
    parsed = urlparse(value)
    return (
        parsed.scheme == "https"
        and (parsed.hostname or "").lower() == host
        and (not path_prefix or unquote(parsed.path).startswith(path_prefix))
        and not parsed.username
        and not parsed.password
    )


def _destination(root: Path, value: str) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        raise ValueError("local_path must be relative")
    destination = (root / raw).resolve()
    allowed = (root / "working" / "images" / "icons").resolve()
    if destination != allowed and allowed not in destination.parents:
        raise ValueError("local_path must be under working/images/icons")
    return destination


def _validate_content(data: bytes, file_format: str) -> str | None:
    if file_format == "png":
        return None if data.startswith(MAGIC["png"]) else "invalid PNG signature"
    if file_format == "svg":
        sample = data.lstrip()
        if not (sample.startswith(b"<svg") or b"<svg" in sample[:500]):
            return "invalid SVG document"
        if SVG_UNSAFE_RE.search(data):
            return "SVG contains active or external content"
        return None
    return f"unsupported format: {file_format}"


def process(manifest_path: Path, download: bool = False) -> list[str]:
    errors: list[str] = []
    root = Path.cwd().resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read manifest: {exc}"]

    icons = manifest.get("icons")
    if not isinstance(icons, list) or not icons:
        return ["manifest must contain a nonempty icons array"]

    seen: set[str] = set()
    for index, icon in enumerate(icons, 1):
        prefix = f"icon {index}"
        if not isinstance(icon, dict):
            errors.append(f"{prefix}: entry must be an object")
            continue
        icon_id = str(icon.get("id", "")).strip()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", icon_id):
            errors.append(f"{prefix}: id must be kebab-case")
        elif icon_id in seen:
            errors.append(f"{prefix}: duplicate id {icon_id}")
        seen.add(icon_id)

        for field in ("product_label", "purpose", "detail_page", "source_url",
                      "official_terms_url", "local_path", "format"):
            if not str(icon.get(field, "")).strip():
                errors.append(f"{prefix}: missing {field}")

        detail_page = str(icon.get("detail_page", ""))
        source_url = str(icon.get("source_url", ""))
        terms_url = str(icon.get("official_terms_url", ""))
        file_format = str(icon.get("format", "")).lower()
        if not _https_host(detail_page, "msicons.com", "/"):
            errors.append(f"{prefix}: detail_page must use https://msicons.com/")
        if not _https_host(source_url, "msicons.com", "/icons/"):
            errors.append(f"{prefix}: source_url must use https://msicons.com/icons/")
        if not _https_host(terms_url, "learn.microsoft.com", "/"):
            errors.append(f"{prefix}: official_terms_url must use Microsoft Learn HTTPS")
        if file_format not in {"svg", "png"}:
            errors.append(f"{prefix}: format must be svg or png")
            continue
        if Path(urlparse(source_url).path).suffix.lower() != f".{file_format}":
            errors.append(f"{prefix}: source extension does not match format")

        try:
            destination = _destination(root, str(icon.get("local_path", "")))
        except ValueError as exc:
            errors.append(f"{prefix}: {exc}")
            continue

        if download and not destination.exists() and not any(error.startswith(prefix) for error in errors):
            try:
                request = Request(source_url, headers={"User-Agent": "PowerPointBuilder/1.0"})
                with urlopen(request, timeout=30) as response:
                    if not _https_host(response.geturl(), "msicons.com", "/icons/"):
                        raise ValueError("download redirected outside msicons.com/icons/")
                    data = response.read(5 * 1024 * 1024 + 1)
                if len(data) > 5 * 1024 * 1024:
                    raise ValueError("download exceeds 5 MB")
                content_error = _validate_content(data, file_format)
                if content_error:
                    raise ValueError(content_error)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
            except Exception as exc:  # network and format failures become validation errors
                errors.append(f"{prefix}: download failed: {exc}")
                continue

        if not destination.is_file():
            errors.append(f"{prefix}: local file not found: {destination.relative_to(root)}")
            continue
        content_error = _validate_content(destination.read_bytes(), file_format)
        if content_error:
            errors.append(f"{prefix}: {content_error}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--download", action="store_true", help="download missing planned files")
    args = parser.parse_args()
    errors = process(args.manifest, args.download)
    if errors:
        print(f"FAIL: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: icon plan and local files validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
