#!/usr/bin/env python3
"""JSONマニフェストとローカル画像から自己完結HTMLギャラリーを生成する。"""
from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_MIME = {"image/png", "image/jpeg", "image/gif", "image/webp"}
IMAGE_SIGNATURES = {
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/gif": (b"GIF87a", b"GIF89a"),
    "image/webp": (b"RIFF",),
}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 50 * 1024 * 1024


def safe_https_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError(f"出典URLは認証情報を含まないHTTPS URLにしてください: {value}")
    return value


def image_data_uri(path: Path) -> tuple[str, int]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"画像ファイルが見つかりません: {path}")
    mime = mimetypes.guess_type(path.name)[0]
    if mime not in ALLOWED_MIME:
        raise ValueError(f"未対応の画像形式です: {path}")
    data = path.read_bytes()
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError(f"画像サイズが範囲外です: {path}")
    if not any(data.startswith(signature) for signature in IMAGE_SIGNATURES[mime]):
        raise ValueError(f"拡張子と画像データが一致しません: {path}")
    if mime == "image/webp" and (len(data) < 12 or data[8:12] != b"WEBP"):
        raise ValueError(f"WebP画像として不正です: {path}")
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}", len(data)


def load_manifest(path: Path) -> dict[str, object]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("categories"), list):
        raise ValueError("manifestにはcategories配列が必要です")
    return manifest


def render(manifest_path: Path) -> str:
    manifest = load_manifest(manifest_path)
    title = html.escape(str(manifest.get("title") or "Image Gallery"))
    categories = manifest["categories"]
    assert isinstance(categories, list)
    nav: list[str] = []
    sections: list[str] = []
    total_bytes = 0
    for category_index, category in enumerate(categories, 1):
        if not isinstance(category, dict) or not isinstance(category.get("images"), list):
            raise ValueError("各categoryにはimages配列が必要です")
        category_name = html.escape(str(category.get("name") or f"Category {category_index}"))
        anchor = f"category-{category_index}"
        nav.append(f'<a href="#{anchor}">{category_name}</a>')
        cards: list[str] = []
        for item in category["images"]:
            if not isinstance(item, dict):
                raise ValueError("imagesの各要素はオブジェクトにしてください")
            image_path = (manifest_path.parent / str(item.get("path") or "")).resolve()
            try:
                image_path.relative_to(manifest_path.parent.resolve())
            except ValueError as exc:
                raise ValueError(f"画像パスはmanifest配下に限定されます: {image_path}") from exc
            data_uri, size = image_data_uri(image_path)
            total_bytes += size
            if total_bytes > MAX_TOTAL_BYTES:
                raise ValueError("画像の合計サイズが50MBを超えています")
            item_title = html.escape(str(item.get("title") or "Untitled"))
            alt = html.escape(str(item.get("alt") or item.get("title") or "Image"), quote=True)
            source = safe_https_url(str(item.get("source_url") or ""))
            source_attr = html.escape(source, quote=True)
            license_note = html.escape(str(item.get("license") or "利用条件未確認"))
            cards.append(
                '<article class="card">'
                f'<img src="{data_uri}" alt="{alt}" loading="lazy">'
                '<div class="meta">'
                f'<h3>{item_title}</h3><p>{license_note}</p>'
                f'<a href="{source_attr}" target="_blank" rel="noopener noreferrer">出典を確認</a>'
                "</div></article>"
            )
        sections.append(
            f'<section id="{anchor}"><h2>{category_name}</h2>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )
    if not sections:
        raise ValueError("1件以上のcategoryが必要です")
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:#f6f7fb;--panel:#fff;--text:#182033;--muted:#586174;--accent:#6657d9;--line:#e3e6ef}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--text);font-family:"Segoe UI","Yu Gothic UI",sans-serif}}
header{{padding:3.5rem clamp(1rem,5vw,5rem) 2rem;background:linear-gradient(135deg,#302b63,#6657d9);color:#fff}}h1{{margin:0 0 .6rem;font-size:clamp(2rem,5vw,4rem)}}header p{{max-width:60rem;margin:0;opacity:.86}}nav{{display:flex;gap:.6rem;flex-wrap:wrap;padding:1rem clamp(1rem,5vw,5rem);position:sticky;top:0;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(12px);z-index:2}}nav a{{padding:.55rem .9rem;border-radius:999px;background:var(--panel);color:var(--accent);text-decoration:none;border:1px solid var(--line)}}main{{padding:1rem clamp(1rem,5vw,5rem) 4rem}}section{{scroll-margin-top:5rem}}h2{{margin:2.5rem 0 1rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.1rem}}.card{{overflow:hidden;border:1px solid var(--line);border-radius:18px;background:var(--panel);box-shadow:0 10px 30px rgba(24,32,51,.08)}}img{{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#dfe3eb}}.meta{{padding:1rem}}h3{{margin:0 0 .55rem;font-size:1.05rem}}.meta p{{color:var(--muted);min-height:2.4em}}.meta a{{color:var(--accent);font-weight:650}}footer{{padding:2rem clamp(1rem,5vw,5rem);color:var(--muted);border-top:1px solid var(--line)}}
@media(prefers-color-scheme:dark){{:root{{--bg:#10131c;--panel:#191e2b;--text:#eef1fa;--muted:#afb7ca;--accent:#b7afff;--line:#30384b}}}}
@media print{{nav{{position:static}}.card{{break-inside:avoid;box-shadow:none}}}}
</style>
</head>
<body><header><h1>{title}</h1><p>カテゴリ別の画像と出典。画像はHTML内に埋め込まれています。</p></header>
<nav aria-label="カテゴリ">{"".join(nav)}</nav><main>{"".join(sections)}</main>
<footer>画像の権利は各権利者に帰属します。利用条件は出典ページで確認してください。</footer></body></html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        output = render(args.manifest.resolve())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8", newline="\n")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
