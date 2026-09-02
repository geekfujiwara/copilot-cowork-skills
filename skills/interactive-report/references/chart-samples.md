# 分析チャートサンプル

すべての例は架空データで、外部ライブラリやネットワーク接続を必要としない。5種類をまとめたHTMLは `scripts/chart_samples.py` で生成できる。

```python
from interactive_report import InteractiveReport

report = InteractiveReport("分析レポート")
```

## バブルチャート

施策の効果、難易度、投資規模など、3変数のポートフォリオ比較に使う。面積の意味を `lead` に明記する。

```python
report.add_bubble_chart(
    "施策ポートフォリオ",
    [
        {"label": "施策A", "x": 35, "y": 82, "size": 60, "group": "成長"},
        {"label": "施策B", "x": 70, "y": 58, "size": 90, "group": "効率"},
    ],
    x_label="実行難易度",
    y_label="期待効果",
    lead="円の大きさは想定投資規模。",
)
```

## ガントチャート

施策の期間、重なり、進捗を示す。日付は `YYYY-MM-DD`、終了日は開始日以降にする。`status` は `complete`、`in-progress`、`planned`、`blocked` を使う。

```python
report.add_gantt_chart("実行計画", [
    {"label": "現状確認", "start": "2026-10-01", "end": "2026-10-14",
     "status": "complete", "owner": "分析担当"},
    {"label": "試行", "start": "2026-10-15", "end": "2026-11-15",
     "status": "planned", "owner": "実行担当"},
])
```

## 概略地図

地域差や拠点分布の概観に使う。緯度は $-90$ から $90$、経度は $-180$ から $180$。同梱地図は簡略図であり、境界、距離、正確な位置、経路の判断には使わない。

```python
report.add_map("地域別の概況", [
    {"label": "地域A", "lat": 35.0, "lng": 135.0, "value": "72"},
    {"label": "地域B", "lat": 48.0, "lng": 8.0, "value": "64"},
])
```

## 棒グラフ

同じ尺度のカテゴリを比較する。`value` はバー幅を表す $0$ から $100$、実際の単位は `display` で明記する。

```python
report.add_bar_chart("カテゴリ別KPI", [
    {"label": "指標A", "value": 72, "display": "72%"},
    {"label": "指標B", "value": 58, "display": "58%", "hl": True},
])
```

## 折れ線グラフ

時系列推移と目標差を示す。各系列で同じ `label` を使い、欠損値は推測で補間しない。

```python
report.add_line_chart("月次推移", [
    {"label": "10月", "value": 52, "series": "実績"},
    {"label": "11月", "value": 61, "series": "実績"},
    {"label": "10月", "value": 60, "series": "目標"},
    {"label": "11月", "value": 68, "series": "目標"},
], y_label="KPI達成率")
```

## 選択と検証

- ランキングに見せる必要がない比較で、順序を恣意的に並べない。
- 軸、単位、対象期間、母数、欠損、目標と実績の区別を表示する。
- 色だけに依存せず、系列名、値、状態をテキストでも示す。
- 地図上の位置やバブルの重なりで値が読めない場合は表を併記する。
- 元データとチャートの点数、最小値、最大値、期間を照合する。
