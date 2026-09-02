#!/usr/bin/env python3
"""Generate a self-contained report demonstrating all bundled chart types."""
from __future__ import annotations

import argparse
from pathlib import Path

from interactive_report import InteractiveReport


def build_sample() -> InteractiveReport:
    report = InteractiveReport(
        "インタラクティブ分析チャート例",
        subtitle="架空データのみ",
        label="SAMPLE",
    )
    report.set_nav_buttons(print_button=True)
    report.add_bubble_chart(
        "施策ポートフォリオ",
        [
            {"label": "施策A", "x": 35, "y": 82, "size": 60, "group": "成長"},
            {"label": "施策B", "x": 70, "y": 58, "size": 90, "group": "効率"},
            {"label": "施策C", "x": 48, "y": 68, "size": 40, "group": "成長"},
        ],
        anchor=("portfolio", "ポートフォリオ"),
        x_label="実行難易度",
        y_label="期待効果",
        lead="円の大きさは想定投資規模。すべて架空値です。",
    )
    report.add_gantt_chart(
        "実行計画",
        [
            {"label": "現状確認", "start": "2026-10-01", "end": "2026-10-14", "status": "complete", "owner": "分析担当"},
            {"label": "試行", "start": "2026-10-15", "end": "2026-11-15", "status": "in-progress", "owner": "実行担当"},
            {"label": "評価", "start": "2026-11-16", "end": "2026-12-10", "status": "planned", "owner": "評価担当"},
        ],
        anchor=("plan", "実行計画"),
    )
    report.add_map(
        "地域別の概況",
        [
            {"label": "地域A", "lat": 35.0, "lng": 135.0, "value": "72"},
            {"label": "地域B", "lat": 48.0, "lng": 8.0, "value": "64"},
            {"label": "地域C", "lat": 38.0, "lng": -97.0, "value": "81"},
        ],
        anchor=("regions", "地域"),
    )
    report.add_bar_chart(
        "カテゴリ別KPI",
        [
            {"label": "指標A", "value": 72, "display": "72%"},
            {"label": "指標B", "value": 58, "display": "58%", "hl": True},
            {"label": "指標C", "value": 84, "display": "84%"},
        ],
        anchor=("kpis", "KPI"),
    )
    report.add_line_chart(
        "月次推移",
        [
            {"label": "10月", "value": 52, "series": "実績"},
            {"label": "11月", "value": 61, "series": "実績"},
            {"label": "12月", "value": 72, "series": "実績"},
            {"label": "10月", "value": 60, "series": "目標"},
            {"label": "11月", "value": 68, "series": "目標"},
            {"label": "12月", "value": 75, "series": "目標"},
        ],
        anchor=("trend", "推移"),
        y_label="KPI達成率",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="working/chart-samples.html")
    args = parser.parse_args()
    output = build_sample().save(Path(args.out))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
