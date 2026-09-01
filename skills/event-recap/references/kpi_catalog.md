# event-recap — KPI カタログ（設計の背景）

コミュニティ／対抗戦型イベントの「開催レポート」で提案・集計すべき KPI とその意味。
案件のリスト列に合わせて `aggregate_attendees.py` の引数にマッピングする。

## 1. 参加規模・チャネル構成
- **総参加者数**（登録ベース＝`IsAttend=true`）。母数の定義を明示する。
- **オンサイト / オンライン比率**。ハイブリッド成功度の指標。
- 拠点別・軍別の内訳（例: `Army` = オンサイト東軍/西軍/オンライン）。
- → `--attend-field IsAttend --choice-fields Army`

## 2. コミュニティの広がり
- **参加企業数**（正規化後・自社除く）。コミュニティの裾野＝最重要 KPI の一つ。
- 上位企業（社別参加人数）。中核企業・スポンサー候補が見える。
- 業界分布（リストに業界列があれば）。
- → `--company-field CompanyName`

## 3. 参加者の質・構成
- **役職構成**（管理職比率）。経営層の関心度の代理指標。
- **ロール構成**（DX推進 / 市民開発 / IT管理 等）。誰に刺さっているか。
- → `--choice-fields Position Role`

## 4. エンゲージメント（能動的参加）
- **競技・ワーク参加率**（例: アプリ早作り対決 `IsAttendRapidPrototyping`）。
- **懇親会参加率**（`IsAttendAfterParty`）。深い関係構築の度合い。
- 登壇数（LT 等）、出題数など当日資料から拾う定性指標。
- → `--bool-fields IsAttendAfterParty IsAttendRapidPrototyping`

## 5. 競技・成果（当日資料 PPTX から）
- 総合結果・各競技スコア、優勝チーム、上位チーム。
- 作成アプリのテーマ、使用ツール（Power Platform / Copilot Studio / エージェント活用率）。

## 6. 今後トラッキングを推奨（初回は測れないことが多い）
- **リピート参加率**（`AttendYear` の年次比較）。継続性 KPI。初回開催では全件同年で測れない旨を注記。
- **満足度 / NPS**（アンケート回収後）。
- ネットワーキングの関心テーマ分布（`NetworkTheme` 等の複数選択列）。

## マッピングの考え方
1. `ListListColumns` で列を確認。
2. 「実参加フラグ」→ `--attend-field`、「カテゴリ列」→ `--choice-fields`、
   「Yes/No 参加列」→ `--bool-fields`、「企業名」→ `--company-field` に割り当て。
3. 出力 JSON を Fact MD の KPI 表へ転記。比率・合計は必ずスクリプト計算値を使う（手計算しない）。
