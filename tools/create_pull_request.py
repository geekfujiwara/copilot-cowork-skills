#!/usr/bin/env python3
"""全品質ゲート通過後にだけブランチを push して Pull Request を登録する。"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def capture(command: list[str]) -> str:
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def execute(command: list[str], label: str) -> None:
    print(f"== {label} ==")
    subprocess.run(command, cwd=ROOT, check=True)


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Pull Request のタイトル")
    parser.add_argument("--body", default="", help="Pull Request の説明")
    parser.add_argument("--body-file", type=Path, help="Pull Request 説明の UTF-8 ファイル")
    parser.add_argument("--base", default="main", help="ベースブランチ（既定: main）")
    parser.add_argument("--draft", action="store_true", help="Draft Pull Request として登録")
    args = parser.parse_args(argv)

    if args.body and args.body_file:
        return fail("--body と --body-file は同時に指定できません")
    if args.body_file:
        try:
            body = args.body_file.read_text(encoding="utf-8")
        except OSError as exc:
            return fail(f"PR 本文を読み込めません: {exc}")
    else:
        body = args.body

    try:
        root = Path(capture(["git", "rev-parse", "--show-toplevel"])).resolve()
        if root != ROOT:
            return fail(f"別の Git リポジトリです: {root}")
        branch = capture(["git", "branch", "--show-current"])
        if not branch:
            return fail("detached HEAD では PR を登録できません")
        if branch == args.base:
            return fail(f"ベースブランチ {args.base!r} から直接 PR は作成できません")

        execute(
            [sys.executable, "-B", "tools/sync_catalog.py"],
            "README・トリガー・依存関係を同期",
        )
        if capture(["git", "status", "--porcelain"]):
            return fail(
                "未コミットの変更があります。自動同期された README.md と "
                "catalog/skills.json を含めてコミットし、再実行してください"
            )

        execute(["git", "fetch", "origin", args.base], "ベースブランチを更新")
        base_ref = f"origin/{args.base}"
        ahead = int(capture(["git", "rev-list", "--count", f"{base_ref}..HEAD"]))
        if ahead < 1:
            return fail(f"{args.base} に対する新しいコミットがありません")

        existing_json = capture([
            "gh", "pr", "list", "--state", "open", "--head", branch,
            "--json", "number,url",
        ])
        existing = json.loads(existing_json or "[]")
        if existing:
            return fail(f"このブランチの PR は既に存在します: {existing[0]['url']}")

        preflight = subprocess.run(
            [sys.executable, "-B", "tools/preflight.py", "--base", base_ref],
            cwd=ROOT,
        )
        if preflight.returncode:
            return fail("公開品質ゲートに失敗したため、push と PR 登録を中止しました")

        execute(["git", "push", "--set-upstream", "origin", branch], "検証済みブランチを push")
        report = (
            "\n\n## 自動事前検証\n\n"
            "- [x] 公開対象ファイルの安全性\n"
            "- [x] README・トリガー・依存関係の同期\n"
            "- [x] 構造・汎用化・秘匿化・参照整合\n"
            "- [x] 回帰テスト\n"
            "- [x] 全スキル監査\n\n"
            f"検証対象: `{base_ref}...{branch}`\n"
        )
        command = [
            "gh", "pr", "create", "--base", args.base, "--head", branch,
            "--title", args.title, "--body", body.rstrip() + report,
        ]
        if args.draft:
            command.append("--draft")
        url = capture(command)
        print(f"PASS: Pull Request を登録しました: {url}")
        return 0
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as exc:
        return fail(f"PR 登録処理に失敗しました: {exc}")


if __name__ == "__main__":
    sys.exit(main())
