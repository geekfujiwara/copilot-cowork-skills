# 同梱フォント

| ファイル | 内容 |
|---|---|
| `assets/fonts/NotoSansJP-VariableFont_wght.ttf` | Noto Sans JP（Version 2.004、可変ウェイト Thin〜Black）。Google Fonts 配布版 |
| `assets/fonts/OFL.txt` | SIL Open Font License 1.1 の全文と著作権表示 |

## ライセンス
Noto Sans JP は SIL Open Font License 1.1 で提供されています。
- 商用利用・動画への使用・ソフトウェアへの同梱・再配布が可能
- 再配布時は `OFL.txt` を必ず同梱すること
- フォント単体での販売は不可。改変版に予約フォント名を使うことは不可
- 作成した動画（成果物）には OFL の制約は及ばない

## フォントの探索順
1. `--font` 引数、または環境変数 `DEMO_VIDEO_FONT`
2. `assets/fonts/` の Noto Sans JP（同梱済み）
3. OS にインストール済みの Noto Sans JP / Noto Sans CJK
4. インターネットから Noto Sans JP を取得（同梱フォントがあれば不要。ネットワーク取得は事前に利用者の承認を取る）
5. 代替: ヒラギノ角ゴ / 游ゴシック / メイリオ（OS 付属。再配布はできないため同梱しない）
