#!/usr/bin/env python3
"""全スキルを dist/<name>.zip へまとめ、ソースとの一致を検証する。"""
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"


def source_files(skill: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(skill.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"シンボリックリンクは使用できません: {path}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files[path.relative_to(skill).as_posix()] = path
    if "SKILL.md" not in files:
        raise ValueError(f"SKILL.md がありません: {skill.name}")
    return files


def package(skill: Path) -> Path:
    archive = DIST / f"{skill.name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as destination:
        for relative, path in source_files(skill).items():
            destination.write(path, relative)
    return archive


def check_archive(skill: Path) -> list[str]:
    archive = DIST / f"{skill.name}.zip"
    if not archive.is_file():
        return [f"不足: {archive.relative_to(ROOT)}"]
    expected = source_files(skill)
    errors: list[str] = []
    try:
        with zipfile.ZipFile(archive) as packaged:
            corrupt = packaged.testzip()
            if corrupt:
                errors.append(f"破損: {archive.name}: {corrupt}")
            names = [item.filename for item in packaged.infolist() if not item.is_dir()]
            if len(names) != len(set(names)):
                errors.append(f"重複エントリ: {archive.name}")
            if set(names) != set(expected):
                missing = sorted(set(expected) - set(names))
                extra = sorted(set(names) - set(expected))
                errors.append(f"内容不一致: {archive.name}: missing={missing}, extra={extra}")
            for name in sorted(set(names) & set(expected)):
                if packaged.read(name) != expected[name].read_bytes():
                    errors.append(f"更新漏れ: {archive.name}: {name}")
    except zipfile.BadZipFile:
        errors.append(f"ZIP破損: {archive.name}")
    return errors


def skills() -> list[Path]:
    return sorted(path for path in SKILLS.iterdir() if path.is_dir())


def check_all() -> int:
    errors: list[str] = []
    current = skills()
    expected_archives = {f"{skill.name}.zip" for skill in current}
    actual_archives = {path.name for path in DIST.glob("*.zip")} if DIST.is_dir() else set()
    extras = sorted(actual_archives - expected_archives)
    if extras:
        errors.append(f"不要なZIP: {', '.join(extras)}")
    for skill in current:
        errors.extend(check_archive(skill))
    if errors:
        print(f"FAIL: {len(errors)} 件")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {len(current)} skills match dist ZIPs")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ZIPを変更せずソースとの一致を検証")
    args = parser.parse_args()
    if args.check:
        return check_all()
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(parents=True)
    for skill in skills():
        print(f"WROTE: {package(skill).relative_to(ROOT)}")
    return check_all()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
