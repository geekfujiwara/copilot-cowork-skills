#!/usr/bin/env python3
"""SKILL.md を単一情報源として README と機械可読カタログを同期する。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import validate_catalog

ROOT = Path(__file__).resolve().parents[1]


def expected_files() -> dict[Path, str]:
    readme_path = ROOT / "README.md"
    return {
        readme_path: validate_catalog.replace_generated_readme_table(
            readme_path.read_text(encoding="utf-8")
        ),
        ROOT / "catalog" / "skills.json": validate_catalog.render_catalog_json(),
    }


def synchronize(check: bool = False) -> list[Path]:
    stale: list[Path] = []
    for path, expected in expected_files().items():
        actual = path.read_text(encoding="utf-8") if path.is_file() else None
        if actual == expected:
            continue
        stale.append(path)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8", newline="\n")
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="更新せず、生成ファイルが最新かだけを検証する",
    )
    args = parser.parse_args(argv)
    try:
        stale = synchronize(args.check)
    except (OSError, ValueError) as exc:
        print(f"FAIL: カタログを同期できません: {exc}", file=sys.stderr)
        return 1

    if stale:
        relative = ", ".join(path.relative_to(ROOT).as_posix() for path in stale)
        if args.check:
            print(f"FAIL: 生成ファイルが最新ではありません: {relative}")
            print("実行: python -B tools/sync_catalog.py")
            return 1
        print(f"UPDATED: {relative}")
    else:
        print("PASS: README と依存関係カタログは最新です")
    return 0


if __name__ == "__main__":
    sys.exit(main())
