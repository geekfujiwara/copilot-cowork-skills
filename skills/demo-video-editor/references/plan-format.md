# edit-plan.json の仕様

| キー | 内容 |
|---|---|
| `name` | 動画名（HyperFrames の title にも使用） |
| `source` | 元動画パス（plan ファイルからの相対パス可） |
| `output` | `width` / `height` / `fps`（既定 1920×1080 / 30）。元動画と比率が違う場合は上下左右に余白を入れる |
| `style` | `font_family`（既定 **Noto Sans JP**）、`accent`（STEP チップ・左帯）、`highlight`（強調枠）、`background`、`callout_accent_bar`（テロップカード左端の装飾帯。既定 false＝表示しない）、`zoom_seconds`（ズーム遷移秒、既定 0.9）、`zoom_margin`（ズーム範囲の余白 px、既定 24） |
| `title` / `end` | タイトル・エンドカード（省略可）。`duration` `kicker` `title` `sub` |
| `segments[]` | 元動画から切り出す区間。出力では順に連結 |

## segments[] の各要素
- `src`: `[開始秒, 終了秒]`（元動画の時刻）
- `mute`: true で音声を消す（任意）
- `zoom`: `[[区間内秒, 範囲], ...]`。範囲は `"full"` か元動画ピクセル座標 `[x0, y0, x1, y1]`。指定時刻から `zoom_seconds` かけて移動。元動画の縦横比に自動で広げてから拡大する
- `callouts`: `[{t:[開始,終了], step, title, sub, position}]`。区間内秒。position は `bottom-left`（既定）/`bottom-right`/`top-left`/`top-right`
- `highlights`: `[{t:[開始,終了], rect:[x0,y0,x1,y1]}]`。元動画ピクセル座標。枠の外側を少し暗くする

## 座標の決め方
`inspect_video.py --at 秒` で書き出したフル解像度フレームを見て、パネルやボタンの左上・右下のピクセル座標を読み取る。
画面が切り替わる（スクロール・遷移する）時刻をまたいで同じ座標を使わないこと。前後 1 秒刻みでフレームを確認する。
