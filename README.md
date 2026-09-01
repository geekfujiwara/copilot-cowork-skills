# Copilot Cowork Skills

Copilot Cowork 向けの再利用可能なコミュニティスキル集です。

標準的な Microsoft 365 アプリと Web 検索のみに依存するスキルを厳選しています。
組織固有のシステムに依存するスキルは含みません。個人情報・組織固有情報はすべて
プレースホルダー化してあります。

## 収録スキル

<!-- BEGIN GENERATED SKILL TABLE -->
| 領域 | スキル | 概要 | 依存先 |
|---|---|---|---|
| 分析 | `event-recap` | PPTX と SharePoint の参加者リストから KPI を集計し、Fact Markdown と自己完結 HTML のイベントレポートを作る。 | SharePoint / PPTX |
| 自動化 | `skill-build` | パーソナルスキルの新規作成・更新に加え、公開前の品質ゲート (汎用化・秘匿化・ コンプライアンス・SKILL.md 簡潔化・参照整合・階層化) を実施する。 | Cowork スキル基盤 |
| 生産性 | `daily-digest` | カレンダー、メール、Teams、文書から本人向けの日次ブリーフィングを作成し、承認後に HTML メールで送信する。 | 予定表 / メール / Teams |
| 生産性 | `deal-brief` | カレンダー、メール、Teams、SharePoint の関連情報を統合し、指定商談の事前ブリーフィングを Markdown で作る。 | 予定表 / メール / Teams / 議事録 / `catalog:ai-digest` / `catalog:client-digest` / `catalog:daily-digest` |
| 生産性 | `self-note` | Teams の「自分とのチャット」へ確認付きで投稿し、許可された範囲のメッセージや添付を取得する。 | Teams |
| 生産性 | `travel-fare` | 公共交通機関の経路検索から片道・往復運賃、所要時間、乗換を概算し、取得元と確度を示す。 | ブラウザ / Web 検索 |
| 調査 | `ai-digest` | 公開 Web から AI・クラウド・業界ニュースを調査し、利用者向けの要約と任意の自己完結 HTML 論点マップを作る。 | Web 検索 |
| 調査 | `client-digest` | 直近の打ち合わせから顧客企業を抽出し、公開情報から AI、業務変革、投資動向を調査して週次レポートを作る。 | 予定表 / メール / Web 検索 / `catalog:daily-digest` |
| 調査 | `gallery` | テーマを複数カテゴリに分け、検索画像をカテゴリ別タブの Adaptive Card ギャラリーとして表示する。 | Web 検索 |
| 文書作成 | `talk-prep` | 登壇依頼を読み、資料収集、シナリオ、タイトル、台本、スライド連携、返信下書きまでを支援する。 | 社内検索 / ファイル読取 |
<!-- END GENERATED SKILL TABLE -->

この一覧と [catalog/skills.json](catalog/skills.json) は各 `SKILL.md` から自動生成されます。
機械可読カタログには説明、トリガー、必要機能、他スキル参照、同梱コンポーネント参照を収録しています。
生成領域を直接編集せず、`python -B tools/sync_catalog.py` で同期してください。

## 命名規則

`<領域>-<動作>` の 2 語まで、小文字ケバブケース、14 文字以内。
同じ領域は接頭辞を揃えています（`*-digest`）。作者名・組織名・製品名・実装技術は
名前に含めません。領域が 1 件だけのものは 1 語です（`gallery` / `self-note`）。

## セットアップ

1. このリポジトリを clone またはダウンロードします
2. `config/placeholders.example.json` を `config/placeholders.json` にコピーし、自分の値を記入します
3. 値を反映したコピーを生成します。`skills/` の原本は変更されません

   ```bash
   python tools/apply_placeholders.py --dry-run   # まず確認
  python tools/apply_placeholders.py             # build/skills に生成
   ```

4. `build/skills/` 配下の各フォルダを OneDrive の `Documents/Cowork/skills/` へコピーします
5. Cowork で新しい会話を開始します（反映まで少し時間がかかります）

必要なスキルだけを選んで導入しても構いません。スキル間に必須依存関係はありません。
他スキルへの任意の委譲は `` `catalog:<name>` `` で明示され、参照先がこのリポジトリ内に
存在することを CI で検証します。名前付きの外部スキルは前提にしません。

### 個別に取り込む場合

Cowork の Customize ページ > Skills タブ > Add の横の矢印 > Upload skill からも
取り込めます。その場合は該当スキルのフォルダを `SKILL.md` がルートに来るよう
zip にしてください。

## プレースホルダー

`{{USER_NAME}}` のような二重波かっこ形式で埋め込まれています。

| キー | 用途 | 使用スキル |
|---|---|---|
| `USER_NAME` | 利用者の氏名 | ほぼ全て |
| `USER_EMAIL` | 送信先のメールアドレス | `daily-digest` / `client-digest` / `self-note` |
| `USER_OBJECT_ID` | 利用者の Entra オブジェクト ID | `self-note` |
| `MANAGER_NAME` | 上長の氏名 | `daily-digest` |
| `COMPANY_DOMAIN` | 自社のメールドメイン（社内外の判定に使用） | `client-digest` |
| `ORG_NAME` | 所属組織名 | `ai-digest` / `talk-prep` |
| `USER_ROLE` | 利用者の役割 | `ai-digest` / `client-digest` |
| `TECH_FOCUS` | 調査・提案で重視する技術領域 | `ai-digest` / `client-digest` |
| `HOME_STATION` | 交通費算出の起点となる駅 | `travel-fare` |
| `OFFICE_STATION` | オフィス最寄り駅 | `travel-fare` |
| `OFFICE_CODE` | オフィスの略称 | `travel-fare` |
| `SHAREPOINT_HOST` | SharePoint のホスト名 | `event-recap` |

`{{N}}` と `{{ABS_PATH_TO_PPTX}}` はスキル本文が実行時に使うテンプレート変数のため、
置換ツールの対象外です。そのままにしてください。

## 前提と制限

- **Copilot Cowork が利用できる環境が必要**です。カスタムスキルは OneDrive の
  `Documents/Cowork/skills/` から読み込まれます（上限 50 スキル）
- `travel-fare` はローカルブラウザ機能を使います
- `event-recap` は参加者リストを SharePoint リストから読みます。列構成は
  自組織のものに合わせて調整してください
- `client-digest` と `daily-digest` はメールを送信します。宛先は既定で本人です
- 各スキルは日本語で記述されています

## 公開前検証

```bash
python -B tools/sync_catalog.py --check
python tools/validate_catalog.py
python -B -m unittest discover -s tests -v
```

組織名、顧客名、内部コードなどの既知の固有語も検査する場合は、Git 管理対象外の
`config/publication-denylist.txt` に 1 行 1 件で記載してから検証します。

## セキュリティとプライバシー

各スキルがアクセスするデータ、外部作用、脆弱性の非公開報告方法は [SECURITY.md](SECURITY.md) を参照してください。

## コントリビューション

スキルの構造、秘匿化、検証、Pull Request の要件は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。
PR は `python -B tools/create_pull_request.py` から登録すると、全品質ゲートの成功前には登録されません。
スキルを追加・更新すると、同コマンドが README と `catalog/skills.json` を自動同期します。
生成差分を含めてコミットするまで PR は登録されず、CI でも同期状態を再検証します。

## ライセンスと注意

- カスタムスキルは Microsoft の検証を受けていません。**内容を確認してから利用してください**
- スキルは AI への指示として動作します。信頼できる提供元からのみ取り込んでください
- 業務手順の記述であり、そのままでは自組織の運用に合わない箇所があります。
  適宜書き換えてお使いください
- コードと文書は [MIT License](LICENSE) で公開しています。外部サービスと任意依存関係は
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) も確認してください
- 初回カタログの作成経緯と公開前処理は [PROVENANCE.md](PROVENANCE.md) に記録しています
