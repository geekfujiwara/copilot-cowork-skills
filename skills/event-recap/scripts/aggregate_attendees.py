#!/usr/bin/env python3
"""
aggregate_attendees.py — SharePoint 参加者リストから KPI を集計する。

汎用イベント開催レポート用。任意の SharePoint リスト（参加者・登録者リスト）の
items JSON から、選択項目・真偽項目・企業名などの分布を集計する。

入力ファイルは次のいずれの形式でも自動判別する:
  (a) MCP QueryGraph の spill ファイル（/workspace/.mcp-results/*.json。
      result.content[0].text に Graph 応答 JSON 文字列が入る）
  (b) Graph の生 items 応答（{"value": [{"fields": {...}}, ...]}）
  (c) fields だけの配列（[{...}, {...}]）

使い方の例:
    python aggregate_attendees.py \
        --files /workspace/.mcp-results/a.json /workspace/.mcp-results/b.json \
        --attend-field IsAttend \
        --choice-fields Army Position Role \
        --bool-fields IsAttendAfterParty IsAttendRapidPrototyping \
        --company-field CompanyName \
        --out output/kpi.json

プレースホルダー（案件ごとに変える箇所）:
    --attend-field   実参加フラグの列名。未指定なら全件を母数にする。
    --choice-fields  分布を出す選択列（例: Army, Position, Role）。
    --bool-fields    参加率を出す真偽列（例: 懇親会・ワーク参加）。
    --company-field  企業名列（正規化してユニーク社数を算出）。
    --ms-keywords    Microsoft 自社を除外する判定キーワード（既定: マイクロソフト Microsoft）。

依存: 標準ライブラリのみ。
"""
import sys
import json
import argparse
from collections import Counter


def load_items(path):
    """spill / 生応答 / 配列 のいずれでも fields の配列を返す。"""
    raw = open(path, encoding="utf-8").read()
    obj = json.loads(raw, strict=False)
    # (a) MCP spill envelope
    if isinstance(obj, dict) and "result" in obj and isinstance(obj["result"], dict):
        txt = obj["result"]["content"][0]["text"]
        obj = json.loads(txt, strict=False)
    # (b) Graph items response
    if isinstance(obj, dict) and "value" in obj:
        return [it.get("fields", it) for it in obj["value"]]
    # (c) plain array
    if isinstance(obj, list):
        return [it.get("fields", it) if isinstance(it, dict) else it for it in obj]
    raise ValueError(f"未対応の形式: {path}")


def normalize_company(name: str) -> str:
    n = (name or "").strip()
    for suf in ("株式会社", "(株)", "（株）", "合同会社", "有限会社"):
        n = n.replace(suf, "")
    return n.replace("　", "").replace(" ", "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--attend-field", default=None)
    ap.add_argument("--choice-fields", nargs="*", default=[])
    ap.add_argument("--bool-fields", nargs="*", default=[])
    ap.add_argument("--company-field", default=None)
    ap.add_argument("--ms-keywords", nargs="*", default=["マイクロソフト", "Microsoft"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = []
    for f in args.files:
        rows += load_items(f)

    result = {"total_records": len(rows)}

    data = rows
    if args.attend_field:
        attending = [r for r in rows if r.get(args.attend_field) is True]
        result["attending"] = len(attending)
        result["not_attending"] = sum(1 for r in rows if r.get(args.attend_field) is False)
        data = attending

    for fld in args.choice_fields:
        c = Counter(r.get(fld, "(未設定)") for r in data)
        result[f"dist_{fld}"] = dict(c.most_common())

    for fld in args.bool_fields:
        yes = sum(1 for r in data if r.get(fld) is True)
        result[f"bool_{fld}"] = {"true": yes, "false": len(data) - yes,
                                 "rate": round(yes / len(data), 3) if data else 0}

    if args.company_field:
        comps = [normalize_company(r.get(args.company_field, "")) for r in data]
        comps = [c for c in comps if c]
        uc = Counter(comps)
        ms_keys = [k for k in uc if any(kw in k for kw in args.ms_keywords)]
        result["companies"] = {
            "unique_normalized": len(uc),
            "unique_excluding_ms": len(uc) - len(ms_keys),
            "ms_records": sum(uc[k] for k in ms_keys),
            "top": dict(uc.most_common(20)),
        }

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(out)
        print(f"WROTE: {args.out}")
    print(out)


if __name__ == "__main__":
    main()
