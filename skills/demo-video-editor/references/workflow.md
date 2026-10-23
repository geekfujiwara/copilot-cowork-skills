---
name: demo-video-editor
description: >
  既存のデモ動画（画面録画）から要所を切り出し、注目箇所へのズーム、強調枠、
  日本語の説明テロップ（STEP 1, 2…）、タイトル／エンドカードを付けたハイライト動画（MP4）を作る。
  既定フォントは同梱の Noto Sans JP。編集内容は edit-plan.json に記録し、ffmpeg + Pillow で MP4 を書き出す。
  依頼があれば同じプランから HyperFrames プロジェクトも生成できる。
  Use when user asks to "デモ動画を編集して", "デモ動画をハイライト編集して", "画面録画にズームと説明を入れて",
  "この動画のポイントをズームして解説を入れて", "デモ動画を短くまとめて", "HyperFrames で動画を編集",
  "demo video highlight", "add zoom and callouts to a screen recording".
  Do NOT use for: 言い間違い・無音の自動カットだけ（video-use 等）、ゼロからのモーショングラフィックス生成、
  会議録画の議事録作成（meeting-intel）、ナレーション音声の生成。
license: MIT
metadata:
  category: productivity
  icon: VideoClip
---

# demo-video-editor

デモ動画の「どこを見せるか」を映像から決め、ズーム・強調枠・日本語テロップで説明を加えたハイライト動画（MP4）を作るスキル。

## When to Use
- 既存の画面録画・製品デモ録画を、要点だけの短いハイライト動画にしたい
- 操作画面の特定箇所を拡大し、日本語の説明テロップ（STEP 形式）を入れたい
- イベント・提案・SNS 用に、デモの見どころを 45〜90 秒程度にまとめたい
- 一度作った編集（edit-plan.json）を、別の録画や文言違いで作り直したい

## When NOT to Use
| 依頼 | 代わりに使うもの |
|---|---|
| 話し言葉の「えー」・言い間違い・無音だけを自動で削りたい | video-use などのカット編集ツール |
| 素材のない状態からアニメーション・モーショングラフィックスを作りたい | HyperFrames / Remotion の作成ワークフロー |
| 会議録画から議事録・要約を作りたい | meeting-intel |
| ナレーション音声や BGM を新たに生成したい | 音声生成ツール（このスキルは元動画の音声のみ使う） |
| 実写映像のカラーグレーディングや複数カメラの編集 | 専用の動画編集ソフト |
| 動画ではなくスライドや静止画の資料を作りたい | pptx / create スキル |

## Inputs and Outputs
- **入力**: 元動画ファイル（MP4 / MOV など ffmpeg で読める形式）。任意で強調したい機能、目標の長さ、タイトル文言
- **出力（既定）**: ハイライト動画 **MP4 1 本のみ**（1920×1080 / 30fps / H.264 + AAC）
- **出力しないもの**: zip などのアーカイブ、作業用ファイル（edit-plan.json・静止画・HyperFrames プロジェクト）は成果物として出さない。
  HyperFrames プロジェクトは、ユーザーが明示的に求めた場合のみ生成して渡す

## 同梱物
| パス | 役割 |
|---|---|
| `scripts/inspect_video.py` | 動画情報、コンタクトシート（一定間隔のサムネイル）、指定時刻のフル解像度フレームを書き出す |
| `scripts/render_preview.py` | edit-plan.json から MP4 を書き出す。`--stills` で指定時刻の静止画だけ確認できる |
| `scripts/build_hyperframes.py` | （依頼時のみ）edit-plan.json から HyperFrames プロジェクトを生成 |
| `scripts/common.py` | ffmpeg 検出、プラン読込、フォント解決（同梱の Noto Sans JP を最優先） |
| `assets/templates/edit-plan.template.json` | 空のプラン雛形 |
| `LICENSE` | このスキルのライセンス（MIT） |
| `references/plan-format.md` | プランの全キーと座標の決め方 |
| `references/editing-guidelines.md` | 構成・ズーム・テロップ・強調枠の基準（必ず読む） |
| `references/hyperframes-notes.md` | HyperFrames の導入・CLI・注意点 |
| `assets/fonts/NotoSansJP-VariableFont_wght.ttf` | 同梱フォント Noto Sans JP（可変ウェイト。テロップ見出しは Bold、補足は Regular で使用） |
| `assets/fonts/OFL.txt` | Noto Sans JP のライセンス（SIL Open Font License 1.1）。フォントを配布・同梱するときは必ず一緒に含める |

必要なツール: `bash`（スクリプト実行）、`view`（コンタクトシート・静止画の目視確認）、成果物の保存（output への MP4 保存）、元動画が OneDrive / SharePoint にある場合はファイル取得ツール。

Required tools（tool ごとの用途）:
- `bash` tool — `inspect_video.py` / `render_preview.py` / `build_hyperframes.py` を実行する
- `view` tool — `contact_sheet.png`、フル解像度フレーム、`--stills` の静止画を目視確認する
- `CopyArtifact`（surface="output"）— 完成した MP4 を `working/demo-edit/` から output へ保存する
- `ReadFileContent` / `SearchM365` — 元動画が OneDrive / SharePoint にある場合に探して取得する
必要環境: Python 3（Pillow, numpy）、ffmpeg（PATH 上、または imageio-ffmpeg）。

スクリプトはこのスキルのフォルダを `SKILL_DIR` として `python "$SKILL_DIR/scripts/<name>.py"` で実行する。
作業ファイルは作業用フォルダ（例: `working/demo-edit/`）に置き、スキルのフォルダには書き込まない。

## 手順

### 1. 素材を把握する
1. 元動画を特定する（添付ファイル、または OneDrive / SharePoint から取得）
2. `python scripts/inspect_video.py VIDEO working/demo-edit/inspect --every 10` を実行し、`contact_sheet.png` を画像として見る
   - 動画が 5 分を超える場合は `--every 20` 程度に広げる
3. 画面の流れ（どの時刻に何の操作・結果が出るか）を時刻付きで書き出す
4. 候補区間の前後を `--at 秒,秒,...` でフル解像度フレームにし、UI パネルやボタンのピクセル座標と、画面が切り替わる時刻を確認する

### 2. 編集プランを提案する
`references/editing-guidelines.md` に従い、次の表をユーザーに示して合意を取る（ユーザーが「お任せ」と言った場合は確認を省略してよい）。

| 出力時刻 | 元動画の区間 | ズーム先 | テロップ（STEP・title・sub） |

- 全体の長さ、STEP 数、タイトル文言、架空データかどうか（kicker に明記）を含める
- テロップには録画に映っている事実だけを書く

### 3. edit-plan.json を書く
`assets/templates/edit-plan.template.json` をコピーして埋める（仕様は `references/plan-format.md`）。
フォントは既定の Noto Sans JP のまま。ユーザーが別フォントを指定した場合のみ `style.font_family` と `--font` を変える。

### 4. 静止画で確認する
```
python scripts/render_preview.py PLAN.json working/demo-edit/out.mp4 --stills 2,10,20,...
```
各区間の「ズーム到着後」と「テロップ表示中」の時刻を選び、生成された静止画を見て次を確認し、必要ならプランを直して再確認する。
- 強調枠が狙った UI に重なっているか（画面のスクロールや遷移でずれていないか）
- テロップが重要な情報を隠していないか（隠す場合は `position` を変える）
- 文字化け（豆腐）がないか

### 5. MP4 を書き出す
```
python scripts/render_preview.py PLAN.json working/demo-edit/<名前>.mp4
```
1080p・60 秒でおよそ数分かかる。完成後、数か所のフレームを抜き出して最終確認する。

### 6. 納品する
- **MP4 だけ**を成果物として保存し、ファイル名で伝える（zip などのアーカイブは出力しない）
- 編集内容の表（ステップ 2 の表）を最終版として示す

## Output Format
納品時のチャット返信は、次の sections で構成した Markdown にする（成果物ファイルは MP4 1 本だけ）。
1. **成果物**: MP4 のファイル名、長さ（秒）、解像度（1920×1080 / 30fps）
2. **編集内容の表**（markdown table）: `| 出力時刻 | 元動画の区間 | ズーム先 | テロップ（STEP・title・sub） |`
3. **確認事項**（bullet）: 代替フォントを使った、架空データ表記の有無など、ユーザーに判断してほしい点。なければ省略
4. HyperFrames プロジェクトを明示的に依頼された場合のみ、そのフォルダ名と「この環境では HyperFrames 未実行」の旨

### （任意）HyperFrames プロジェクト
ユーザーが「HyperFrames でも書き出したい」「プロジェクトがほしい」と明示した場合のみ:
```
python scripts/build_hyperframes.py PLAN.json working/demo-edit/<name>-hyperframes
```
フォントと OFL.txt がプロジェクト内に同梱される。書き出しは利用者の環境で HyperFrames CLI を使って行う（README の手順を参照）。
この環境で HyperFrames 自体を実行していない場合は、そう明記する。

## Guardrails
- **元動画がない・読めない（if the source video is missing or cannot be read）**: 推測で作らない（never fabricate）。ファイル名を示して再添付を依頼する。スクリプトが「元動画が見つかりません」で止まったら source のパスを直す
- **内容を作らない（never invent content）**: テロップ・タイトルには録画に映っている事実だけを書く。映っていない製品名・技術名・数値・効果を足さない
- **座標は推測しない（always verify on a full-resolution frame）**: 強調枠とズーム範囲は必ずフル解像度フレームで確認してから決める
- **フォント（never bundle OS fonts）**: 同梱の Noto Sans JP（SIL OFL 1.1）を使う。同梱フォントが欠けて代替フォントを使った場合はユーザーに伝える。OS 付属フォント（游ゴシック・メイリオ等）は再配布できないので同梱しない
- **映像内容（no content filtering）**: 元動画に映っている内容のフィルタリングや自動マスキングは行わない。公開前の確認は利用者に委ねる（「利用上の注意」を参照）
- **デザイン既定（do not show the accent bar by default）**: テロップカード左端の装飾帯は既定で表示しない（`style.callout_accent_bar: false`）。ユーザーが求めた場合のみ true にする
- **長い処理（fallback: re-run the same command if rendering fails）**: 元動画全体は読み込まず、区間ごとにデコードする。書き出しが途中で止まった場合は同じコマンドを再実行する
- **プラン合意（show the plan before rendering）**: MP4 を書き出す前にステップ 2 の編集プラン表を示して合意を取る（confirm before rendering）。ユーザーが「お任せ」と言った場合のみ省略できる
- **環境の不足（if ffmpeg is not found or Pillow/numpy are unavailable）**: 書き出しを試み続けず、不足しているものを伝えて導入を依頼する（ask the user）。imageio-ffmpeg があればそれを使う
- **成果物の形式（never output zip archives）**: 既定の成果物は MP4 1 本だけ。edit-plan.json・静止画・HyperFrames プロジェクトは明示的な依頼がない限り渡さない

## 利用上の注意
利用者向けの案内です（このスキルが確認・ブロックするものではありません）。
- 元動画に映っている内容の権利・公開可否は、利用者の責任で判断してください
- 公開前に、顧客名・個人名・メールや通知のポップアップ・URL バー・社内データ・認証情報などが映り込んでいないかを確認することを推奨します
- このスキルは映像内容のフィルタリングや自動マスキングは行いません

## ライセンス
- このスキル（SKILL.md・scripts・references・templates）は MIT License で提供します（`LICENSE` を参照）
- 同梱フォント Noto Sans JP は SIL Open Font License 1.1 のままで、MIT の対象外です（`assets/fonts/OFL.txt` を参照）
