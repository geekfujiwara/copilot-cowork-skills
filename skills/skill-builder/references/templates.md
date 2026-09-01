# 雛形タイプの選び方（scaffold --type）

`scaffold_skill.py --type {...}` で選べる 4 つの雛形。いずれも採点器が評価する要素
（トリガー句・Do NOT use・When NOT to Use・番号付きワークフロー・出力フォーマット・
Guardrails）を最初から含む。迷ったら作るスキルの「主目的」で選ぶ。

| type | 主目的 | 例 | 既定 category / icon の例 |
|------|--------|----|--------------------------|
| `aggregation` | M365 データを集約して提示 | 日次ブリーフィング、進捗まとめ、横断検索 | productivity / DataPie |
| `writing` | コンテンツを作成（読者向け） | 状況共有メール、議事録、レポート草案 | writing / DocumentEdit |
| `decision` | 状況を分析し段階的に推奨 | カレンダー整理、優先度付け、トリアージ | analysis / Lightbulb |
| `basic` | 上記に当てはまらない汎用 | 任意のワークフロー固定化 | custom / Sparkle |

## 生成例

```bash
# 集約系
python scripts/scaffold_skill.py --name weekly-digest --type aggregation \
  --category productivity --icon DataPie --summary "週次の進捗を集約して提示する"

# 作成系
python scripts/scaffold_skill.py --name status-mail --type writing \
  --category writing --icon DocumentEdit --summary "状況共有メールを作成する"

# 意思決定支援系
python scripts/scaffold_skill.py --name calendar-triage --type decision \
  --category analysis --icon Lightbulb --summary "予定を分析し対応を推奨する"
```

## 命名規則

| スタイル | 例 | 使いどころ |
|----------|----|-----------|
| `verb-noun` | `send-status`, `track-expenses` | 行動指向 |
| `context-action` | `weekly-review`, `meeting-prep` | 反復ワークフロー |
| `domain-specific` | `vendor-invoice-tracker` | 狭いスコープ |

**規則**: kebab-case、先頭は英数字、最大 64 文字。利用環境の予約名を避け、上書きせず別名を使用する。

## 記入のコツ（採点を上げる）

- **トリガー句は 4〜6 個**、実際にユーザーが言いそうな表現で。日本語・英語の両方を混ぜる。
- **Do NOT use 行**で別スキルへ委譲する場合は、同じカタログに存在する名前を `catalog:<name>` 形式で記載する。
- **ツールは具体名で**指定する（「適当なツール」ではなく `SearchM365` 等）。
- **出力フォーマット**（長さ・構成・例）を必ず書く。
- **過学習しない**: トリガーが外れたら逐語句ではなく広い概念を足す。
- 詳細な品質基準は同梱の [publish-readiness.md](publish-readiness.md) を参照。
