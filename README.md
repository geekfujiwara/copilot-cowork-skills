<div align="center">

# ✨ Copilot Cowork Skills

**仕事の調査・整理・準備を、再利用できるCoworkスキルに。**

[![Validate catalog](https://github.com/geekfujiwara/copilot-cowork-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/geekfujiwara/copilot-cowork-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-2563EB.svg)](LICENSE)

[インストール](#インストール) · [スキル一覧](#スキル一覧) · [使い方](#使い方) · [フィードバック](#フィードバック)

</div>

---

## このリポジトリについて

Copilot Coworkで利用できる、日本語中心のコミュニティスキル集です。予定表、メール、Teams、
SharePoint、OneDrive、Officeファイル、公開Webなどを横断し、業務に使えるMarkdownやレポートへ整理します。

- **すぐ試せる** — 必要なスキルだけZIPでアップロード
- **個人設定ファイル不要** — 氏名、メール、所属などは実行時コンテキストから取得
- **安全優先** — 外部入力を命令として扱わず、送信・申請・公開は確認または下書きまで
- **更新漏れ防止** — 説明、トリガー、依存関係、READMEを自動検証

> [!IMPORTANT]
> カスタムスキルはMicrosoftによる検証済み製品ではありません。内容とアクセス対象を確認し、
> 組織のポリシーに従って利用してください。

## インストール

### 方法A — AIに準備を任せる（推奨）

VS CodeのGitHub Copilotなど、GitとPythonを実行できるコーディングエージェントへ次を依頼します。

> `geekfujiwara/copilot-cowork-skills` をcloneし、READMEの一覧から私の用途に合うスキルを提案してください。
> 選んだスキルを `python -B tools/package_skills.py <skill-name...>` でCoworkアップロード用ZIPにし、
> 作成されたファイルの場所を教えてください。ファイルの内容は変更しないでください。

AIが作成した `dist/<skill-name>.zip` を、次の手順でアップロードします。

1. Copilot Coworkを開く
2. **Customize** → **Skills** を開く
3. **Add** の横にある矢印 → **Upload skill** を選ぶ
4. `dist` フォルダーのZIPを1つ選ぶ
5. 必要なスキルごとに繰り返し、新しいCowork会話で試す

### 方法B — コマンドで準備する

1. このリポジトリをcloneまたはZIPダウンロードして展開
2. リポジトリ直下で次を実行

   ```bash
   # 全スキルをパッケージ化
   python -B tools/package_skills.py

   # 必要なものだけパッケージ化（例）
   python -B tools/package_skills.py business-trip image-gallery event-recap
   ```

3. 方法Aの手順2〜5で、`dist` に生成されたZIPをアップロード

各ZIPは、展開した直下に `SKILL.md` が来るCowork向け構造です。個人用の `config` 作成や値の置換は不要です。

### OneDriveで配置する場合

組織のCowork環境がOneDriveからのスキル読込に対応している場合は、ZIPではなく
`skills/<skill-name>/` フォルダーをそのまま `Documents/Cowork/skills/<skill-name>/` へコピーします。
組織設定によって利用できない場合があるため、通常は **Upload skill** を推奨します。

## スキル一覧

<!-- BEGIN GENERATED SKILL TABLE -->
| 領域 | スキル | 概要 | 依存先 |
|---|---|---|---|
| 分析 | `event-recap` | ユーザーが指定または添付した資料と参加者データから KPI を集計し、根拠付き Markdown のイベントレポートを作る。 | ファイル読取 / Excel / CSV / JSON / SharePoint / OneDrive |
| 自動化 | `skill-builder` | パーソナルスキルの新規作成・更新に加え、公開前の品質ゲート (汎用化・秘匿化・ コンプライアンス・SKILL.md 簡潔化・参照整合・階層化) を実施する。 | Cowork スキル基盤 |
| 生産性 | `business-trip` | 予定表、メール、会議、社内資料、公開情報から出張要件と規定を集め、公共交通の経路・運賃概算、宿泊、申請、関係者、資料を統合したMarkdown旅程を作る。 | Outlook予定表 / メール / Teams / 会議議事録 / SharePoint / OneDrive / ブラウザ / Web検索 / 社内検索 / ファイル読取 |
| 生産性 | `daily-digest` | カレンダー、メール、Teams、文書から本人向けの日次ブリーフィングを作成し、承認後に HTML メールで送信する。 | 予定表 / メール / Teams |
| 生産性 | `deal-brief` | カレンダー、メール、Teams、SharePoint の関連情報を統合し、指定商談の事前ブリーフィングを Markdown で作る。 | 予定表 / メール / Teams / 議事録 / `catalog:client-digest` / `catalog:daily-digest` / `catalog:digest-news` |
| 生産性 | `self-note` | Teams の「自分とのチャット」へ確認付きで投稿し、許可された範囲のメッセージや添付を取得する。 | Teams |
| 調査 | `client-digest` | 直近の打ち合わせから顧客企業を抽出し、公開情報から AI、業務変革、投資動向を調査して週次レポートを作る。 | 予定表 / メール / Web 検索 / `catalog:daily-digest` |
| 調査 | `digest-news` | 公開 Web から AI・クラウド・業界ニュースを調査し、利用者向けの要約と任意の自己完結 HTML 論点マップを作る。 | Web 検索 |
| 調査 | `image-gallery` | テーマ別に検索した画像を安全に取得し、カテゴリ、出典、代替テキスト付きの自己完結HTMLギャラリーとして表示する。 | Web 検索 / ファイル作成 / HTML表示 |
| 文書作成 | `talk-prep` | 登壇依頼を読み、資料収集、シナリオ、タイトル、台本、スライド連携、返信下書きまでを支援する。 | 社内検索 / ファイル読取 |
<!-- END GENERATED SKILL TABLE -->

詳細なトリガー、必要機能、他スキル参照、同梱ファイルは
[catalog/skills.json](catalog/skills.json) に機械可読形式で収録しています。

## 使い方

インストール後は、新しいCowork会話で自然に依頼します。

| やりたいこと | 依頼例 |
|---|---|
| 出張計画 | 「来週の大阪出張を、社内規定と会議予定に沿って計画して」 |
| イベント集計 | 「添付のExcelと当日資料からイベントレポートを作って」 |
| 画像収集 | 「新製品画像をカテゴリ別のギャラリーにして」 |
| 商談準備 | 「明日の顧客会議の商談ブリーフィングを作って」 |
| 日次整理 | 「今日の予定と重要メールをブリーフィングにして」 |

Coworkが必要な情報へアクセスできない場合は、対象ファイルを会話へ添付するか、アクセス権のある保存場所を指定します。
スキルは権限を迂回せず、確認できない情報を推測しません。

## データと安全性

- スキルは利用者が既にアクセスできる情報だけを読みます
- 必要な期間、ファイル、列に範囲を限定します
- メール、文書、Web検索結果に含まれる命令文を実行しません
- 個人情報、予約番号、決済情報、シークレットを成果物へ不要に転載しません
- 送信、投稿、共有、公開、予約、購入、申請、削除は自動実行しません
- 内部情報を公開Webの検索語へ含めません

問題を報告するときは、秘密情報、個人情報、社内URL、実データをIssueへ貼らないでください。

## 開発と品質チェック

スキルを追加・更新した場合は、READMEと依存関係カタログを同期してから検証します。

```bash
python -B tools/sync_catalog.py
python -B tools/preflight.py
```

CIでも同じチェックが実行されます。`SKILL.md`を単一情報源として、READMEの一覧と
[catalog/skills.json](catalog/skills.json) を生成します。生成領域は直接編集しません。

## フィードバック

このスキル集を使った感想は、Xの [@geekfujiwara](https://x.com/geekfujiwara) へぜひお寄せください。
不具合や改善要望は [GitHub Issues](https://github.com/geekfujiwara/copilot-cowork-skills/issues) で受け付けます。

> [!NOTE]
> このリポジトリではPull Requestを受け付けていません。改善案はIssueへお願いします。
> IssueやXでは、実在する顧客名、会議内容、メール、内部URL、シークレットを共有しないでください。

建設的で敬意あるコミュニケーションをお願いします。嫌がらせ、差別、個人情報の公開、攻撃的な投稿には対応しません。

## ライセンス

コードと文書は [MIT License](LICENSE) で公開しています。外部サービスや第三者素材には、それぞれの利用条件が適用されます。

---

<div align="center">

**Built for practical work with Copilot Cowork.**

</div>
