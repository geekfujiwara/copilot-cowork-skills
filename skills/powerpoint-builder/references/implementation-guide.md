# PPTXGenJS Implementation Guide

## Runtime contract

- Node.jsと `pptxgenjs` を使用する。
- 生成スクリプトは作業ディレクトリへ作成し、入力と出力を相対パスまたはコマンド引数で受け取る。
- 同梱テンプレートはサンプルであり、そのまま完成資料として使用しない。
- ユーザー名、組織名、ブランド、ロゴ、出力先を固定値にしない。
- 画像生成物は `working/images/generated/`、取得したアイコンは `working/images/icons/` へ先に配置する。

```javascript
const pptxgen = require("pptxgenjs");
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = process.env.PRESENTATION_AUTHOR || "";
pptx.subject = "<確認済みの主題>";
pptx.title = "<確認済みのタイトル>";
```

## Editable-first construction

テキスト、表、グラフ、プロセス図は、可能な限りPowerPointのネイティブ要素で作成する。スクリーンショットで全面を画像化しない。画像を使う場合は、利用条件、形式、解像度、縦横比を確認する。

## Notes and citations

話者向け補足は `slide.addNotes()` に入れる。引用や統計にはスライド内で短い出典を付け、完全な書誌情報は出典スライドへまとめる。内部資料は公開URLへ変換せず、利用者が識別できる資料名と更新日を記録する。

## Layout helpers

テンプレートのヘルパーは次を保証する。

- 安全な余白と一貫したタイトル位置
- 14pt以上の本文
- カード間隔と整列
- 出典領域
- 前景色と背景色のコントラスト

本文の3カードと区切りページは `scripts/deck-template.js` の `addCard()` と `addSectionDivider()` を基にする。階層・成熟度図は `scripts/hierarchy_diagram.py` の `add_hierarchy_diagram()`、ロングテール分析は `scripts/long_tail_diagram.py` の `add_long_tail_diagram()` を作業用生成コードから呼び出す。両Pythonヘルパーは `--out` で単独サンプルも生成できる。

## Generation

`scripts/deck-template.js` を作業ディレクトリへコピーし、プレースホルダーを置換して実行する。未置換の `{{...}}` が残る場合は成果物を発行しない。

テンプレートは次の環境変数で検証済みローカル画像を受け取る。

| 変数 | 用途 |
|---|---|
| `PRESENTATION_GENERATED_DIR` | 生成した背景・イラストのフォルダー。既定は `working/images/generated` |
| `PRESENTATION_ICON_DIR` | 取得済みアイコンのフォルダー。既定は `working/images/icons` |
| `PRESENTATION_COVER_IMAGE` | 生成画像フォルダー内の表紙背景ファイル名 |
| `PRESENTATION_CARD_IMAGE_1`〜`3` | 生成画像フォルダー内の8:3カード挿絵ファイル名 |
| `PRESENTATION_ICON_1`〜`3` | アイコンフォルダー内のカード用ファイル名 |

パスは指定フォルダー内へ制限し、存在しないファイルでは生成を停止する。リモートURLを `addImage()` へ渡さない。アイコンの正式な製品名は `ICON_1_LABEL`〜`3` のプレースホルダーへ設定する。

```text
node working/create-presentation.js
python scripts/validate_pptx.py working/presentation.pptx
```

実行環境にNode.jsまたは依存パッケージがない場合は、利用可能なPowerPoint生成機能へ切り替えるか、不足を利用者へ報告する。パッケージを無断でグローバルインストールしない。
