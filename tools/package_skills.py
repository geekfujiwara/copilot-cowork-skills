#!/usr/bin/env python3
"""選択したCoworkスキルをアップロード可能なZIPへまとめる。"""
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
DEFAULT_OUTPUT = ROOT / "dist"


def package(skill: Path, output: Path) -> Path:
    archive = output / f"{skill.name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as destination:
        for path in sorted(skill.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"シンボリックリンクはパッケージ化できません: {path}")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                destination.write(path, path.relative_to(skill).as_posix())
    return archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", help="スキル名。省略時は全スキル")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    available = {path.name: path for path in SKILLS.iterdir() if path.is_dir()}
    selected = args.skills or sorted(available)
    missing = sorted(set(selected) - set(available))
    if missing:
        print(f"FAIL: スキルが見つかりません: {', '.join(missing)}", file=sys.stderr)
        return 1
    output = args.output.resolve()
    dist = DEFAULT_OUTPUT.resolve()
    inside_repo = ROOT == output or ROOT in output.parents
    allowed_in_repo = output == dist or dist in output.parents
    if output in ROOT.parents or (inside_repo and not allowed_in_repo):
        print("FAIL: リポジトリ内の出力先はdist配下だけ指定できます", file=sys.stderr)
        return 1
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)
    try:
        for name in selected:
            print(f"WROTE: {package(available[name], output)}")
    except (OSError, ValueError) as exc:
        print(f"FAIL: パッケージ化できません: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
