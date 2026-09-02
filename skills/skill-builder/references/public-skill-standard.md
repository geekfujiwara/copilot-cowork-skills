# 公開スキル標準

この公開リポジトリの現行 `skills/*` を、作成・更新時の構造・安全性・実行品質の標準とする。特定スキルをコピーするのではなく、用途に近い実装パターンを参照する。

## 参照する標準パターン

- `catalog:account-plan`: 社内規定、成功事例、Teams、Outlook、SharePoint等から前提を取得し、AskUserQuestion、KPI、予算、実行計画、自己完結HTMLへつなぐ業務計画
- `catalog:business-trip`: 組織規定、申請経路、過去実績、公開情報を区別する計画
- `catalog:daily-brief`: 継続会話、単一履歴、差分配信、重複防止、スケジュール実行
- `catalog:event-recap`: 複数入力形式、KPI定義、母数・欠損・根拠の検算
- `catalog:talk-prep`: 組織の指定様式、過去成功パターン、下書きで止める外部作用
- `catalog:image-gallery`: 安全な取得、入力検証、自己完結HTML
- `catalog:self-chat`: 最小権限、本人限定、送信確認

## 作成・更新の判定

1. 最も近い標準パターンを一つ以上選び、必要な品質要件だけを取り込む。
2. 環境固有値を埋め込まず、実行時コンテキストから取得する。
3. 詳細を `references/`、再現可能な処理を `scripts/` に分け、`SKILL.md` を判断と導線に限定する。
4. 業務判断を伴う場合は `publish-readiness.md` の業務コンテキストゲートを適用する。
5. 作成・更新後、対象監査と全スキルZIP生成・照合を行う。`dist` はローカル生成物としてGit管理しない。
6. FAIL 0の場合だけPRを作成する。PRのCIでも全スキル監査とZIP生成・照合を再実行する。
7. main反映後にGitHub Actionsが全ZIPをGitHub Releaseへ登録する。

既存標準と異なる設計が必要な場合は、理由、安全策、検証方法をPRへ記載する。
