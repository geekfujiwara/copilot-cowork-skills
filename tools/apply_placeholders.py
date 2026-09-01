#!/usr/bin/env python3
"""設定値を反映したスキルを build/skills に生成する（原本は変更しない）。"""
import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
CONF = ROOT / "config" / "placeholders.json"
DEFAULT_OUTPUT = ROOT / "build" / "skills"
TEXT_EXT = {'.md', '.py', '.js', '.json', '.txt', '.yml', '.yaml', '.csv'}
TOKEN = re.compile(r'\{\{([A-Z_0-9]+)\}\}')

# スキル本文が意図的に使うテンプレート変数（置換対象外）
SKIP = {'N', 'ABS_PATH_TO_PPTX'}


def load_config(path):
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    config = {key: value for key, value in raw.items() if not key.startswith("_")}
    for key, value in config.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key}: 空でない文字列を指定してください")
        if "\n" in value or "\r" in value or "{{" in value or "}}" in value:
            raise ValueError(f"{key}: 改行またはプレースホルダー構文は使用できません")
    return config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--config', type=Path, default=CONF)
    ap.add_argument('--output', type=Path, default=DEFAULT_OUTPUT,
                    help='生成先（既定: build/skills）')
    args = ap.parse_args()

    if not args.config.is_file():
        sys.exit(f'設定が見つかりません: {args.config}\n'
                 'config/placeholders.example.json をコピーして作成してください。')

    try:
        conf = load_config(args.config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        sys.exit(f"設定が不正です: {exc}")

    output = args.output.resolve()
    if output == SOURCE.resolve() or SOURCE.resolve() in output.parents:
        sys.exit('生成先を skills/ 配下には指定できません。原本を保護するため処理を中止します。')
    if not args.dry_run:
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(SOURCE, output, symlinks=False)

    changed, applied, unknown = 0, collections.Counter(), collections.Counter()
    scan_root = SOURCE if args.dry_run else output
    for path in scan_root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXT:
            continue
        src = path.read_text(encoding='utf-8')

        def sub(match):
            key = match.group(1)
            if key in SKIP:
                return match.group(0)
            if key in conf:
                applied[key] += 1
                return conf[key]
            unknown[key] += 1
            return match.group(0)

        out = TOKEN.sub(sub, src)
        if out != src:
            changed += 1
            if not args.dry_run:
                path.write_text(out, encoding='utf-8')

    print(f'{"[dry-run] " if args.dry_run else ""}更新ファイル: {changed}')
    print(f'置換したプレースホルダー: {sum(applied.values())} 箇所 / {len(applied)} 種類')
    if unknown:
        print('未設定のまま残ったキー: ' +
              ', '.join(f'{k}({v})' for k, v in unknown.most_common()))
        return 1
    if not args.dry_run:
        print(f'生成先: {output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
