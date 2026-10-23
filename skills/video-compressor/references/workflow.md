---
name: video-compressor
description: >
  動画ファイル（MP4/MOV/MKV/AVI/WebM など）を ffmpeg で圧縮し、ファイルサイズを小さくした MP4
  （H.264 + AAC、faststart）を作る。目標サイズ（〇MB 以下）指定なら 2-pass、指定なしなら画質プリセット（CRF）で圧縮し、
  既定で 1080p（短辺 1080、縦動画も可）・30fps を品質下限として維持し、下回る縮小は明示指示時のみ。圧縮前後を表で報告する。
  Use when user asks to "動画を圧縮して", "動画を軽くして", "ファイルサイズを小さくして",
  "メールで送れるサイズにして", "Teams に上げられるサイズに", "〇MB 以下にして",
  "compress this video", "reduce video file size".
  Do NOT use for: ハイライト編集・ズーム・テロップ（demo-video-editor を使う）、会議録画の議事録作成、新しい動画の制作。
license: MIT
metadata:
  category: productivity
  icon: VideoClip
---

# video-compressor

動画を「見た目をなるべく保ったまま」小さくし、メール・Teams・PowerPoint でそのまま使える MP4 にするスキル。
エンジンは ffmpeg / ffprobe、処理は同梱の `scripts/compress_video.py` にまとめてある。

## When to Use
- 画面録画・デモ録画・スマホ動画が大きすぎて、メール添付やチャット共有ができない
- 「20MB 以下に」「メールで送れるサイズに」など、目標サイズが決まっている
- 画質をある程度保ちつつ、とにかく軽くしたい（目標サイズなし）
- MOV / MKV / AVI / WebM を、互換性の高い MP4 に変換しつつ小さくしたい

## When NOT to Use
| 依頼 | 代わりに使うもの |
|------|------------------|
| ハイライト編集・ズーム・強調枠・テロップ入れ | demo-video-editor |
| 会議録画から議事録・要約を作る | 会議要約系スキル（例: meeting-intel） |
| ゼロから新しい動画・アニメーションを作る | 動画制作系スキル（本スキル対象外） |
| 動画のカット・結合・トリミングが主目的 | demo-video-editor（圧縮だけが目的なら本スキル） |

## 品質下限（既定ルール）
- **解像度**：短辺 1080 を下限として維持（横 1920×1080 / 縦 1080×1920 / その他の比率も短辺で判定）。アスペクト比は常に維持し、偶数ピクセルにする
- **fps**：30fps 相当を下限として維持
- 元が下限を超える（4K・1440p・60fps など）→ 短辺 1080・30fps までの縮小は可。既定ではそれ未満にしない
- 元が下限以下（720p・24fps など）→ 元のまま。拡大・fps の引き上げはしない
- 目標サイズモードでも下限は維持し、**ビットレートだけ**を下げる（自動で解像度・fps を落とさない）
- 下限未満（720p・15fps など）への圧縮は、**ユーザーが明示的に指示した場合のみ**許可（`--allow-below-floor`）

## 入力
- ユーザーがアップロードした動画ファイル（`input/` 配下など）
- OneDrive / SharePoint 上の動画：`sharepoint_onedrive` の `SearchDrive` / `GetDriveItem` で特定し、`ReadFileContent` 等で作業フォルダ `working/` に取得してから処理する
- 対象ファイルが複数・曖昧な場合は、候補（ファイル名・サイズ・更新日）を示して 1 回だけ確認する

## Workflow

1. **確認（ffprobe）** — 長さ・解像度・fps・ビットレート・コーデック・サイズを取得し、短く提示する。
   ```bash
   ffprobe -v error -show_format -show_streams -print_format json "<input>"
   ```
   （ffprobe が無い環境では同梱スクリプトが `ffmpeg -i` の出力から同じ情報を取る）
2. **モード決定**
   - **(a) 目標サイズ**（「〇MB 以下」「メールで送れるサイズ」）→ 2-pass H.264。
     映像ビットレート = 目標サイズ × 8 × 0.95（安全マージン）÷ 長さ − 音声ビットレート。
     「メールで送れるサイズ」のように数値が無い場合は、一般的な添付上限の目安として 20MB 前後を提案し、
     実際の上限は組織の設定次第である旨を添える（具体的な上限値を断定しない）。
   - **(b) 画質プリセット**（目標サイズなし）→ CRF。既定は **標準**。
     | プリセット | CRF (H.264) | 用途 |
     |---|---|---|
     | 高画質 | 23 | 見た目をほぼ保つ |
     | 標準（既定） | 28 | 共有用の一般的なバランス |
     | 最小 | 32 | とにかく小さく |
3. **解像度・fps（品質下限を守る）**
   - 既定：短辺 1080・30fps を上限として適用（`--max-short-side 1080 --fps 30`）。下限以下の元動画はそのまま
   - 目標サイズに対し映像ビットレートが低すぎる（目安 1080p/30fps で 1.5 Mbps 未満）場合も、解像度・fps は維持して
     ビットレートだけを下げる。報告で「画質が劣化する可能性がある」こと、「1080p / 30fps 未満への縮小は指示があれば可能」
     「音声削除（`--no-audio`）も有効」であることを伝える。720p 等への自動縮小・提案の先回りはしない
   - ユーザーが「720p にして」「15fps でいい」など明示的に指示した場合のみ
     `--max-short-side 720 --fps 15 --allow-below-floor` のように下限未満を指定する
   - 音声：AAC 96〜128 kbps。依頼があれば音声を削除（`--no-audio`）
   - 画面録画（スライド・操作画面）は `--screen`（x264 `-tune animation`）、静止画中心のスライド録画は `--screen --static`（`-tune stillimage`）
4. **エンコード** — 既定は H.264（libx264）+ yuv420p + `-movflags +faststart`（Teams・Outlook・PowerPoint で広く再生可）。
   H.265 はユーザーが明示的に求めた場合のみ（`--codec h265`、互換性が下がる点を一言伝える）。
   ```bash
   # 目標サイズ
   python scripts/compress_video.py "<input>" --target-mb 20 --screen
   # 画質プリセット（既定で短辺 1080・30fps を維持）
   python scripts/compress_video.py "<input>" --preset 標準
   # ユーザーが明示的に下限未満を指示した場合のみ
   python scripts/compress_video.py "<input>" --max-short-side 720 --fps 15 --allow-below-floor
   ```
   主な引数：`input` `[output]` `--target-mb` `--preset {高画質,標準,最小}` `--max-short-side`（短辺上限、既定 1080。
   旧 `--max-height` は短辺として扱う互換別名） `--fps`（既定 30） `--allow-below-floor` `--no-audio` `--audio-kbps` `--codec {h264,h265}` `--screen` `--static` `--speed`。
   1080 未満・30fps 未満を `--allow-below-floor` なしで指定すると、スクリプトは実行を拒否してメッセージを返す。
   スクリプトは `scripts/` からの相対パス（スキルフォルダ内）で呼び出す。長い動画は時間がかかるため `initial_wait` を長めに取る。
5. **検証** — スクリプトが JSON で返す `checks` を確認する。
   - `target_size_ok`：目標超過なら自動で低いビットレートで再エンコード（最大 2 回）。それでも超える場合は音声削除を提案し、
     1080p / 30fps 未満への縮小は「指示があれば可能」と伝えるにとどめる
   - `duration_ok`：元と長さが一致（±1 秒 / 1%）
   - `playable`：ffmpeg で先頭をデコードできる
   - `quality_warning` があれば、画質劣化の可能性を必ず報告する
   - 出力が元より大きい場合は「既に十分圧縮済み」と伝え、元ファイルの利用か、より強い設定を提案する
6. **報告** — 下の出力形式で短く報告する。

## 出力形式
- 成果物は **MP4 のみ**。ファイル名は `<元のファイル名>_compressed.mp4`。`working/` で作成し `output/` に公開する
- zip などのアーカイブは、ユーザーが明示的に求めた場合以外は作らない
- 報告は次の Markdown table（解像度 / fps の前後を必ず含める）+ 1〜2 行のコメント（画質の見込み、品質下限を維持したか、さらに小さくする余地など）

| 項目 | 圧縮前 | 圧縮後 |
|---|---|---|
| サイズ | 68.0 MB | 4.8 MB（-93.0%） |
| 解像度 / fps | 3840×2160 / 60 | 1920×1080 / 30 |
| ビットレート | 27.2 Mbps | 1.9 Mbps |
| コーデック | H.264 / AAC | H.264 / AAC |

## Guardrails
- 元ファイルは上書き・削除しない（Never overwrite or delete the original; output is always a new file）
- OneDrive/SharePoint へのアップロード・メール送信は、ユーザーが求めた場合のみ（Never upload or auto-send; confirm before sharing）
- 動画の内容を編集・カットしない。長さが変わったら失敗として扱い報告する（Do not alter content; a duration mismatch is a failure）
- 確認できないサイズ上限を断定しない。「一般に 20〜25MB 前後が目安」程度に留める（Never fabricate platform limits）
- 品質下限（短辺 1080 = 1920×1080 / 1080×1920、30fps）を既定で必ず維持し、アスペクト比を変えない。拡大・fps 引き上げもしない（Never go below 1080p/30fps by default; never upscale）
- 下限未満への縮小は、ユーザーが明示的に指示した場合のみ `--allow-below-floor` で行う。自動で解像度・fps を落とさない（Only go below the floor on explicit instruction）
- 目標サイズが極端に小さく画質が大きく落ちる場合は、圧縮前に見込みを伝え、音声削除などの代案と「指示があれば 1080p / 30fps 未満も可能」を示す（Confirm before a heavy quality loss）
- 入力が見つからない・動画として読めない場合は、推測で進めずファイルの再指定を依頼する（If the input is missing or cannot be read, ask the user）
- ffmpeg がエラーで失敗した場合は、エラー要約と代替設定（`--speed fast`、`--codec h264` など、品質下限内の設定）を示して再試行する（If encoding fails, report and fall back）
- 成果物は MP4 のみ。zip 等のアーカイブは明示的な依頼がない限り作らない（Always deliver MP4 only; do not zip unless asked）
- 用語：体験型の研修を指す場合は「インタラクティブなワークショップ」と表記する
- 同梱スクリプト以外のツールのインストールやネットワーク取得は行わない（Do not install tools or fetch from the network）

## Common Issues
| 症状 | 原因 | 対処 |
|---|---|---|
| 目標サイズを超える | 動きの多い映像・低すぎる目標 | 自動再試行後も超える場合 `--no-audio`。1080p / 30fps 未満（例 `--max-short-side 720 --allow-below-floor`）はユーザーの指示がある場合のみ |
| 画質が粗い（目標サイズモード） | 1080p/30fps に対しビットレート不足 | 下限は維持したまま報告。目標サイズの緩和・音声削除を提案し、下限未満は指示があれば可能と伝える |
| 文字がにじむ（画面録画） | ビットレート不足 | `--screen`、`--static`、解像度・fps は下限（1080p / 30fps）を維持 |
| 「品質下限を下回る指定です」で停止 | 1080 未満・30fps 未満を指定 | ユーザーの明示的な指示を確認したうえで `--allow-below-floor` を付ける |
| 縦動画が横向きの解像度で判定される | 旧 `--max-height` の高さ基準 | 短辺基準の `--max-short-side` を使う（スマホの回転メタデータも考慮済み） |
| 「width not divisible by 2」 | 奇数解像度 | スクリプトが自動で偶数化（手動時は `scale=trunc(iw/2)*2:trunc(ih/2)*2`） |
| Mac / 一部アプリで再生不可 | H.265 や yuv444p | 既定の H.264 + yuv420p を使う |
