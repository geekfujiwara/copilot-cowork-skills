# event-recap — 異常系・落とし穴と対処（背景つき）

実運用で踏んだ罠と、その回避策。案件が変わっても同じ問題が起きるため、ここに集約する。

## 1. SharePoint リスト取得の spill が 100KB で壊れる ★最重要

**症状**：`QueryGraph` で `$expand=fields`（全列）＋`$top=100` を取ると、spill ファイル
（`/workspace/.mcp-results/*.json`）の `result.content[0].text` が **ちょうど char 102400（100KB）で切れ**、
`json.loads` が `Unterminated string` / `Invalid control character` で失敗する。

**原因**：MCP のツール結果テキストが 100KB で切り詰められる。1 ページの応答がこれを超えると内部 JSON が破断する。

**対処**：
- **必要列だけ** `$expand=fields($select=col1,col2,...)` で取る。全列は取らない。
- **ページサイズを下げる**（`$top=60` 程度）。8 列×60 件で約 50KB に収まり安全。
- パースは `json.loads(text, strict=False)`。
- それでも切れる場合は列をさらに減らす／`$top` を下げる。

## 2. ページング skiptoken で 400 になる

**症状**：`@odata.nextLink` を見て `$skiptoken=Paged=TRUE&p_ID=109`（デコード値）を渡すと
`invalidRequest (400)`。

**対処**：nextLink 末尾の **base64 トークンをそのまま** 渡す（例: `UGFnZWQ9VFJVRSZwX0lEPTEwOQ`）。
`$select`／`$expand`／`$top` も nextLink と同じものを併せて渡すこと。

## 3. spill ファイルの場所と形

- 置き場所は **`/workspace/.mcp-results/`**（Bash の cwd は呼び出しごとに `/mnt/workspace` にリセットされるので絶対パスで参照）。
- 形：`{"jsonrpc","id","result":{"content":[{"type":"text","text":"<Graph応答JSON文字列>"}]}}`。
  `scripts/aggregate_attendees.py` はこの envelope・生 Graph 応答・fields 配列のいずれも自動判別する。

## 4. 企業名の表記ゆれ（ユニーク社数 KPI が水増しされる）

**症状**：「デンソー」「株式会社デンソー」、「ダイハツ工業」「ダイハツ工業株式会社」が別社として数えられ、
ユニーク企業数が過大になる（生データ 80 件 → 実体は約 59 件）。

**対処**：`scripts/aggregate_attendees.py` の `normalize_company()` が `株式会社/(株)/合同会社/有限会社`・
空白・全角空白を除去して正規化。`--ms-keywords` で自社（Microsoft）を別計上。
特殊な合併・略称は案件ごとに alias を足す余地あり（スクリプト内コメント参照）。

## 5. PPTX が大容量（数十 MB）

**症状**：当日資料が 80MB+ のことがある。`ReadFileContent` はバイナリを `grounding/downloads/` に保存するだけ。

**対処**：`scripts/extract_pptx.py` で本文・表・ノートをテキスト抽出。画像は無視（ファクトはテキスト＋ノートに十分ある）。

## 6. HTML 生成機能が実行されないことがある

**症状**：利用環境の HTML 生成機能を呼び出しても処理されずに返ることがある。

**対処**：サブエージェントに任せず、**`generate.py`／`validate.py` を直接 Bash で実行**する（SKILL.md 手順 6）。
report テンプレートの vars は `title`（必須）＋`sections`（`heading/body/items?/table?`）。

## 7. Teams 会議チャットの画像取得（hostedContents）

- `ListChatMessages` ツールは**整形テキスト**を返し、画像参照は含まれない。画像を取るには
  **`QueryGraph(/chats/{realId}/messages, $select=id,from,body,...)` の生 JSON** を使い、
  body 内の `hostedContents/{id}/$value` を正規表現で拾う。
- chat の**実 ID**（`19:meeting_...@thread.v2`）が必要。`ListChats` の spill から取得（会議の joinUrl の base64 と一致）。
- ダウンロード：`QueryGraph(path=".../hostedContents/{id}/$value", query_params={})` を叩くと
  バイナリが `grounding/downloads/<id>.png` に保存される（QueryGraph は $value のバイナリをファイル保存してくれる）。
- **メッセージのページング**：`$skiptoken`（base64）は `$select` と併用すると 400。次ページは `$top`＋`$skiptoken` のみ。
- `hostedContents` の一覧（`/$value` なし）は `contentBytes:null` を返すだけ。実体は必ず `/$value`。

## 8. 外部共有 OneDrive フォルダの写真取得

- 他テナント/別ユーザーの共有フォルダでも `GetDriveChildren(web_url=<共有リンク>)` で一覧できる。
- ただし一覧が作る `drive/files/file_N/...` は **0byte の placeholder**。実体は入っていない。
- 実バイトは `GetDriveItem(web_url=フォルダ)` で `drive_id` を得て、各ファイルの item_id（一覧テキストの `ID:`）で
  **`ReadFileContent(drive_id, item_id)`** を呼ぶ（→ `grounding/downloads/` に保存）。
- 大量にある場合（数百枚）は全部取らず、時刻（ファイル名の iOS UTC タイムスタンプ）で代表数枚を選ぶ。

## 9. 採点・アンケート xlsx

- 投票配点が区分で異なる（審査員5・参加者1 など）→ `scripts/aggregate_scoring.py`。
- フォーム外の票（口頭確認など）は `--manual` で手動加算し、レポートに**加算した旨を明記**（誠実性）。
- アンケート自由記述は**原文のまま保持**し、良い/改善点/中立に分類。改善提案を含む回答は「改善点」へ。

## 10. 参加者数の定義に注意（レポートの誠実性）

- 「参加者数」は **登録リスト（`IsAttend=true`）ベース**。当日の実参加とは差が出うる。
- カレンダー招待者数（例: 181）とリスト件数（例: 177）は**別物**。混同しない。
- Microsoft 運営スタッフはリスト未登録が多く、`Role=Microsoft` の件数は実態より少ない。
- Fact MD・HTML には必ず**データ前提の注記**を入れる。
