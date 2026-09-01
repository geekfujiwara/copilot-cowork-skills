#!/usr/bin/env python3
"""
aggregate_scoring.py — 投票/採点アンケート（xlsx）を重み付きで集計する。

汎用イベント開催レポート用。審査員と一般参加者で配点が異なる投票
（例: 審査員5点・参加者1点）を集計し、チーム別合計点と順位を出す。

使い方:
  python aggregate_scoring.py <xlsx> \
      --voter-col "あなたは審査員ですか、一般参加者ですか？" \
      --choice-col "一番良いと思ったチームを選んでください" \
      --weight 審査員=5 --weight 一般参加者=1 \
      [--manual "チーム名=5"]   # フォーム外の口頭票などを手動加算

プレースホルダー（案件で変える箇所）:
  --voter-col   投票者区分の列名（見出し行の文字列、完全一致）。
  --choice-col  投票先（チーム）の列名。
  --weight      区分=点数 を繰り返し指定。未指定の区分は1点。
  --manual      集計後に手動加算する票（例: りなたむ氏の口頭票）。複数可。

依存: openpyxl（プリインストール）。
"""
import argparse
from collections import defaultdict


def main():
    import openpyxl
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("--voter-col", required=True)
    ap.add_argument("--choice-col", required=True)
    ap.add_argument("--weight", action="append", default=[])
    ap.add_argument("--manual", action="append", default=[])
    ap.add_argument("--sheet", default=None)
    args = ap.parse_args()

    weights = {}
    for w in args.weight:
        k, v = w.split("=", 1)
        weights[k] = float(v)

    wb = openpyxl.load_workbook(args.xlsx, data_only=True)
    ws = wb[args.sheet] if args.sheet else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h) if h is not None else "" for h in rows[0]]
    vi = header.index(args.voter_col)
    ci = header.index(args.choice_col)

    score = defaultdict(float)
    by_type = defaultdict(lambda: defaultdict(int))
    total_votes = 0
    for r in rows[1:]:
        team = r[ci]
        if not team:
            continue
        vt = r[vi]
        score[team] += weights.get(vt, 1)
        by_type[team][vt] += 1
        total_votes += 1

    for man in args.manual:
        team, pts = man.split("=", 1)
        # 既存キーに部分一致させる
        match = [t for t in score if team in t] or [team]
        score[match[0]] += float(pts)
        by_type[match[0]]["(手動)"] += 1
        print(f"# 手動加算: {match[0]} += {pts}")

    print(f"\n総投票数(フォーム): {total_votes}")
    print(f"配点: {weights}")
    print(f"\n{'順位':>3} {'チーム':40} {'合計点':>6}  内訳")
    for rank, (t, s) in enumerate(sorted(score.items(), key=lambda x: -x[1]), 1):
        detail = " / ".join(f"{k}:{v}" for k, v in by_type[t].items())
        print(f"{rank:>3} {t:40} {int(s):>6}  {detail}")


if __name__ == "__main__":
    main()
