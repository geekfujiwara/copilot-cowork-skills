#!/usr/bin/env python3
"""Pull Request 登録前と CI で共通利用する公開品質ゲート。"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 1024 * 1024
FORBIDDEN_EXACT = {
    "config/placeholders.json",
    "config/publication-denylist.txt",
}
FORBIDDEN_DIRS = {"build", "output", "working", "__pycache__"}


def run(command: list[str], label: str) -> bool:
    print(f"\n== {label} ==")
    completed = subprocess.run(command, cwd=ROOT, text=True)
    if completed.returncode:
        print(f"FAIL: {label} (exit {completed.returncode})")
        return False
    print(f"PASS: {label}")
    return True


def tracked_files() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    )
    return [item.decode("utf-8") for item in completed.stdout.split(b"\0") if item]


def forbidden_reason(relative: str) -> str | None:
    path = PurePosixPath(relative)
    lowered = relative.lower()
    if relative in FORBIDDEN_EXACT:
        return "実値を含むローカル設定"
    if any(part in FORBIDDEN_DIRS for part in path.parts):
        return "生成物またはキャッシュ"
    if lowered.endswith((".pyc", ".zip")):
        return "生成物または元アーカイブ"
    if path.name == ".env" or (
        path.name.startswith(".env.") and not path.name.endswith(".env.example")
    ):
        return "実値を含む環境設定"
    return None


def validate_tracked_files() -> bool:
    print("\n== Git 管理対象の安全性 ==")
    failures: list[str] = []
    for relative in tracked_files():
        reason = forbidden_reason(relative)
        if reason:
            failures.append(f"{relative}: {reason}")
            continue
        path = ROOT / relative
        if path.is_file() and path.stat().st_size > MAX_FILE_BYTES:
            failures.append(f"{relative}: 1 MiB を超えています")
    if failures:
        print("FAIL: 公開対象に禁止ファイルがあります")
        for failure in failures:
            print(f"- {failure}")
        return False
    print("PASS: 禁止設定・生成物・ZIP・巨大ファイルなし")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        help="差分検証の基準 Git ref（例: origin/main）。省略時は作業ツリーを検証",
    )
    args = parser.parse_args(argv)

    passed = validate_tracked_files()
    diff_command = ["git", "diff", "--check"]
    if args.base:
        diff_command.append(f"{args.base}...HEAD")
    passed = run(diff_command, "Git whitespace 検証") and passed
    passed = run(
        [sys.executable, "-B", "tools/sync_catalog.py", "--check"],
        "README・トリガー・依存関係の同期検証",
    ) and passed
    passed = run(
        [sys.executable, "-B", "tools/validate_catalog.py"],
        "カタログ検証（構造・秘匿・参照を含む）",
    ) and passed
    passed = run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        "回帰テスト",
    ) and passed

    for skill in sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir()):
        passed = run(
            [
                sys.executable,
                "-B",
                "skills/skill-build/scripts/audit_skill.py",
                str(skill),
            ],
            f"スキル監査: {skill.name}",
        ) and passed

    print("\n== 最終結果 ==")
    print("PASS: PR 登録可能" if passed else "FAIL: PR を登録できません")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
