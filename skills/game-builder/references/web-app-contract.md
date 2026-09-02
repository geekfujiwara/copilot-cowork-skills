# Web App Contract

## 構成

```text
<game-slug>/
  index.html
  README.md
  score-schema.json
  resources/
    assets-manifest.json
    css/app.css
    js/app.js
    images/
```

すべて相対パスで参照し、主要ゲームは `file://` で開いても動くプレーンHTML/CSS/JavaScriptを既定とする。モジュール、fetch、Service Workerなどローカルファイルで制限される機能を使う場合は、READMEにローカルサーバー起動方法を併記する。

## UIテーマ

最初のスクリプトでURLの `scoutTheme` またはOS設定からlight/darkを選び、`data-theme` を設定する。色は `--cp-bg`、`--cp-surface`、`--cp-border`、`--cp-text`、`--cp-text-muted`、`--cp-accent`、`--cp-success`、`--cp-danger`、`--cp-warning`、`--cp-link` などのCSS変数だけを使う。フォントは `"Segoe UI", Aptos, Calibri, sans-serif` とする。

## 必須機能

- タイトル、目的、遊び方、開始、進行、結果、再挑戦
- 現在の進捗とスコアの視覚・テキスト表示
- キーボードとタッチ操作、フォーカス表示、代替テキスト
- 音を使う場合の既定オフまたは明確なミュート
- ランキング、JSONエクスポート・インポート・消去
- エラー表示と安全な初期状態への復帰

## 禁止

CDN、外部フォント、リモート画像、解析タグ、広告、埋め込みトークン、`eval`、ユーザー入力の未エスケープHTML挿入を使わない。外部通信が必要な共有ランキングはローカル版と分離する。
