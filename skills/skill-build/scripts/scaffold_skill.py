#!/usr/bin/env python3
"""scaffold_skill.py — 汎用スキル雛形ジェネレータ (stdlib only).

新規パーソナルスキルのディレクトリと SKILL.md 雛形をワンショットで生成する。
採点器が評価する要素（トリガー句・Do NOT use・When NOT to Use・番号付き
ワークフロー・出力フォーマット・Guardrails）を最初から埋め込むため、
生成直後でも構造検証を通り、MVB に近い状態から記入を始められる。

正常系のみを担当する。異常（名前衝突・上限到達など）は終了コードと
人間可読メッセージで返し、呼び出し側 (SKILL.md / references) が処理する。

使い方:
  python scaffold_skill.py --name weekly-status \
      --type writing --category writing --icon DocumentEdit \
      --summary "毎週の進捗レポートを作成する"

  # 既知の雛形を一覧
  python scaffold_skill.py --list-types

終了コード:
  0  成功
  2  入力エラー（名前不正・上限到達・既存ディレクトリ 等 = 異常系）
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# --- 定数 ----------------------------------------------------------------
PERSONAL_SKILLS_ROOT = Path(
    os.environ.get("COWORK_SKILLS_ROOT", "/mnt/user-config/skills")
)
BUILTIN_SKILLS_ROOT = Path(
    os.environ.get("COWORK_BUILTIN_SKILLS_ROOT", "/opt/workspace-config/.github/skills")
)
NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$")
SKILL_LIMIT = 50
# ディレクトリ名で衝突を避けたいビルトイン名（参考。完全な一覧ではない）
RESERVED_PREFIXES = {
    "pdf", "docx", "xlsx", "pptx", "html", "email", "calendar-management",
    "daily-briefing", "meeting-intel", "schedule-meeting", "render-ui",
    "stakeholder-comms", "skills", "deep-reasoning", "deep-research",
}

TYPES = ("aggregation", "writing", "decision", "basic")

# description 長チェックの閾値（文字数）
DESC_RECOMMENDED = 300   # 推奨上限（description は 300 文字以下）
DESC_HARD_LIMIT = 1024   # システムのハード上限（超過すると skill validation が失敗）


# --- 雛形本文 ------------------------------------------------------------
def _frontmatter(name: str, summary: str, category: str, icon: str,
                 delegate: str) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"category: {category}\n"
        "triggers:\n"
        "  - [トリガー句1]\n"
        "  - [トリガー句2]\n"
        "  - [trigger phrase]\n"
        "capabilities:\n"
        "  - [必要な機能]\n"
        "description: |\n"
        f"  {summary} Use when user asks to \"[トリガー句1]\", \"[トリガー句2]\",\n"
        "  \"[トリガー句3]\", \"[トリガー句4]\".\n"
        f"  Do NOT use for [対象外のケース] — use {delegate} instead.\n"
        "cowork:\n"
        f"  category: {category}\n"
        f"  icon: {icon}\n"
        "---\n"
    )


def _body_aggregation() -> str:
    return """
## Overview
[使用するデータソースと、何を生成するかを 2 文で要約]

## When to Use
- [トリガーになる状況 1]
- [トリガーになる状況 2]

## When NOT to Use
- [対象外のケース] — use [別スキル] instead

## Quick Start
```
User: "[依頼例]"
1. コンテキスト取得: 実行ユーザー・タイムゾーンを確認
2. データ取得: [SearchM365 / 具体的なツール + パラメータ]
3. 結果をフィルタ・分類
4. 下記フォーマットで出力
```

## Core Instructions
### Step 1: コンテキスト取得
[呼び出すツールと、抽出する値]
### Step 2: データ取得
[正確なパラメータ付きのツール呼び出し]
### Step 3: 提示
[出力フォーマット — markdown テンプレートまたは表]

## Output
[長さ・構成・例]

## Guardrails
- 書き込み系アクションの前に必ずユーザーへ提示する
- データが無い場合は「無い」と明示する — 捏造しない
- [ドメイン固有の制約]
"""


def _body_writing() -> str:
    return """
## Overview
[何を、誰向けに作成するか]

## When to Use
- [トリガーになる状況 1]
- [トリガーになる状況 2]

## When NOT to Use
- [対象外のケース] — use [別スキル] instead

## Quick Start
```
User: "[依頼例]"
1. 対象読者と目的を確認（未指定なら）
2. コンテキスト取得: [メール・ファイル・会議]
3. 下記フォーマットで草案を作成
4. 送信前にレビュー用として提示
```

## Core Instructions
### Step 1: コンテキスト取得
[根拠となる情報を横断検索]
### Step 2: 草案作成
[トーン・構成・節立て]
### Step 3: 提示
[送信前にユーザー確認]

## Output
- トーン: [フォーマル / 会話的]; 長さ: [範囲]; 構成: [見出し]

## Guardrails
- 送信前に必ず草案をレビュー用として提示する
- 第三者コンテンツを転載しない。未確認の主張は [要確認] と記す
- [ドメイン固有の制約]
"""


def _body_decision() -> str:
    return """
## Overview
[何を分析し、どの意思決定を支援するか]

## When to Use
- [トリガーになる状況 1]
- [トリガーになる状況 2]

## When NOT to Use
- [対象外のケース] — use [別スキル] instead

## Quick Start
```
User: "[依頼例]"
1. ファクト収集: [ツール呼び出し]
2. 分類 / スコアリング
3. 根拠付きで段階的に推奨
4. 確認が取れた場合のみ実行
```

## Core Instructions
### Step 1: ファクト収集
### Step 2: 分類 / スコアリング
### Step 3: 推奨（段階的・根拠付き）
### Step 4: 実行（確認後のみ）

## Output
[引用根拠付きの段階的な推奨]

## Guardrails
- 変更を実行する前に必ず確認する
- すべての推奨に根拠（出典）を添える
- [ドメイン固有の制約]
"""


def _body_basic() -> str:
    return """
## Overview
[このスキルが何をするかを 2 文で要約]

## When to Use
- [トリガーになる状況 1]
- [トリガーになる状況 2]

## When NOT to Use
- [対象外のケース] — use [別スキル] instead

## Quick Start
```
User: "[依頼例]"
1. [ステップ 1: 具体的な行動とツール]
2. [ステップ 2]
3. 下記フォーマットで出力
```

## Core Instructions
### Step 1: [見出し]
[呼び出すツールと抽出する値]
### Step 2: [見出し]
[正確なパラメータ]
### Step 3: 提示
[出力フォーマット]

## Output
[長さ・構成・例]

## Guardrails
- 不可逆・破壊的な操作の前には確認する
- データが無い場合は「無い」と明示する — 捏造しない
- [ドメイン固有の制約]
"""


BODIES = {
    "aggregation": _body_aggregation,
    "writing": _body_writing,
    "decision": _body_decision,
    "basic": _body_basic,
}


# --- 検証ヘルパ ----------------------------------------------------------
def _die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    """異常系: 人間可読メッセージを出して終了コード 2 で抜ける。"""
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def _validate_name(name: str) -> None:
    if not NAME_RE.match(name):
        _die(
            f"名前 '{name}' が不正です。kebab-case（英数字・ハイフン・"
            "アンダースコア・ドット、先頭は英数字、最大 64 文字）にしてください。"
        )
    if name in RESERVED_PREFIXES:
        _die(
            f"名前 '{name}' はビルトインスキルと衝突します。別名にするか、"
            "SKILL.md 内で明示的に上書き宣言してください（references/error-flows.md 参照）。"
        )


def _check_count(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))


def _extract_description(md_text: str) -> str | None:
    """SKILL.md の frontmatter から description 文字列を取り出す（yaml 優先・stdlib fallback）。"""
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = parts[1]
    try:
        import yaml  # 環境にあれば正確（validate_skill.py と同じ計測になる）
        data = yaml.safe_load(fm)
        if isinstance(data, dict) and data.get("description") is not None:
            return str(data["description"]).strip()
    except Exception:
        pass
    # fallback: | / > ブロック、またはインライン description を素朴に解釈
    style = None
    buf: list[str] = []
    base = None
    capturing = False
    for line in fm.splitlines():
        if not capturing:
            m = re.match(r"^description:\s*([|>]?)\s*(.*)$", line)
            if not m:
                continue
            style, inline = m.group(1), m.group(2)
            if inline and not style:
                return inline.strip().strip("\"'")
            capturing = True
            continue
        if line.strip() and re.match(r"^\S", line):  # 次のトップレベルキー（cowork: 等）
            break
        if line.strip() == "":
            buf.append("")
            continue
        indent = len(line) - len(line.lstrip())
        if base is None:
            base = indent
        buf.append(line[base:] if len(line) >= base else line.strip())
    if style == ">":
        return " ".join(x.strip() for x in buf if x.strip()).strip()
    return "\n".join(buf).strip()


def check_description(path: str) -> int:
    """description 長を 300（推奨）/1024（ハード上限）で判定。

    戻り値: 0 = PASS/WARN（非致命）, 2 = FAIL（ハード上限超過 = validation が落ちる）。
    """
    p = Path(path)
    if not p.exists():
        _die(f"'{path}' が見つかりません。")
    desc = _extract_description(p.read_text(encoding="utf-8"))
    if desc is None:
        _die("frontmatter に description が見つかりません。")
    n = len(desc)
    print(f"description length: {n} 文字（推奨 <= {DESC_RECOMMENDED} / ハード上限 {DESC_HARD_LIMIT}）")
    if n > DESC_HARD_LIMIT:
        print(f"  FAIL: ハード上限 {DESC_HARD_LIMIT} を超過。skill validation が失敗します。必ず短縮してください。")
        return 2
    if n > DESC_RECOMMENDED:
        print(f"  WARN: 推奨 {DESC_RECOMMENDED} 文字を超過（{n}）。トリガー句を精選し 300 文字以下へ短縮を推奨。")
        return 0
    print("  PASS: 300 文字以下です。")
    return 0


# --- メイン --------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="新規パーソナルスキルの雛形を生成する（正常系のみ）。"
    )
    ap.add_argument("--name", help="スキル名（= ディレクトリ名、kebab-case）")
    ap.add_argument("--type", choices=TYPES, default="basic",
                    help="雛形タイプ（既定: basic）")
    ap.add_argument("--category", default="custom",
                    help="cowork category（productivity/communication/analysis/"
                         "writing/research/automation/custom）")
    ap.add_argument("--icon", default="Sparkle", help="Fluent UI アイコン名（PascalCase）")
    ap.add_argument("--summary", default="[このスキルが何をするかを一文で]",
                    help="description 冒頭の一文サマリ")
    ap.add_argument("--delegate", default="the built-in skills skill",
                    help="Do NOT use 行で委譲先として記す別スキル名")
    ap.add_argument("--root", default=str(PERSONAL_SKILLS_ROOT),
                    help="パーソナルスキルのルート（既定: %(default)s）")
    ap.add_argument("--with-references", action="store_true",
                    help="references/ ディレクトリも作成する")
    ap.add_argument("--with-scripts", action="store_true",
                    help="scripts/ ディレクトリも作成する")
    ap.add_argument("--force", action="store_true",
                    help="既存ディレクトリがあっても SKILL.md を上書きする")
    ap.add_argument("--list-types", action="store_true",
                    help="利用可能な雛形タイプを表示して終了")
    ap.add_argument("--check-desc", metavar="SKILL_MD",
                    help="既存 SKILL.md の description 長を 300（推奨）/1024（ハード上限）でチェックして終了")
    args = ap.parse_args(argv)

    if args.list_types:
        print("利用可能な雛形タイプ:")
        for t in TYPES:
            print(f"  - {t}")
        return 0

    if args.check_desc:
        return check_description(args.check_desc)

    if not args.name:
        _die("--name は必須です（--list-types を除く）。")

    # --- 正常系チェック ---
    _validate_name(args.name)
    root = Path(args.root)
    count = _check_count(root)
    if count >= SKILL_LIMIT:
        _die(f"スキル数が上限 {SKILL_LIMIT} に達しています（現在 {count}）。"
             "古いスキルを削除してください。")

    skill_dir = root / args.name
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists() and not args.force:
        _die(f"'{skill_md}' は既に存在します。--force で上書きできます。")

    # --- 生成 ---
    skill_dir.mkdir(parents=True, exist_ok=True)
    content = _frontmatter(
        args.name, args.summary, args.category, args.icon, args.delegate
    ) + BODIES[args.type]()
    skill_md.write_text(content, encoding="utf-8")

    references = skill_dir / "references"
    references.mkdir(exist_ok=True)
    troubleshooting = references / "troubleshooting.md"
    if not troubleshooting.exists():
        troubleshooting.write_text(
            "# Troubleshooting\n\n異常系、原因、対処、恒久チェックを記録する。\n",
            encoding="utf-8",
        )
    if args.with_scripts:
        (skill_dir / "scripts").mkdir(exist_ok=True)

    # --- description 長の自己チェック（300 推奨 / 1024 ハード上限）---
    print("--- description 長チェック ---")
    check_description(str(skill_md))

    # --- 次の一手を提示 ---
    builtin = str(BUILTIN_SKILLS_ROOT / "skills" / "scripts")
    this = "scripts/scaffold_skill.py"
    print(f"OK: {skill_md} を生成しました（type={args.type}, 既存スキル数={count}）。")
    print("次の手順:")
    print(f"  1. SKILL.md の [...] プレースホルダを実際の内容に置き換える（description は 300 文字以下を厳守）")
    print(f"  2. description 長: python {this} --check-desc {skill_md}")
    print(f"  3. 構造検証:      python {builtin}/validate_skill.py {skill_md}")
    print(f"  4. 採点:          python {builtin}/score_skill.py {skill_md} --json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
