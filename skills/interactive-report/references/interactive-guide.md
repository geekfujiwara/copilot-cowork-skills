# Interactive Report 実装ガイド

`scripts/interactive_report.py`（`InteractiveReport`）と `scripts/interactive.css` の
API・実装ルール・落とし穴をまとめる。SKILL.md の Option A-i の詳細版。

---

## 1. 基本

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from interactive_report import InteractiveReport

r = InteractiveReport('タイトル', subtitle='サブ', label='REPORT', date='<対象日>')
```

- `Report` を継承しているため、静的レポートのメソッドはすべてそのまま使える。
- `build()` が `report.css` → `interactive.css` → JavaScriptの順で自動的に埋め込む。
- 出力は完全自己完結型（外部 CSS / JS / 画像なし）。ブラウザと利用可能な構文検査で確認する。

---

## 2. API リファレンス

### `set_nav_buttons(expand_all=True, print_button=True)`
ナビ右端のボタンを設定。`expand_all` はアコーディオンの一括開閉（ラベルが自動で
「すべて閉じる」に切り替わる）、`print_button` は `window.print()`。

### `add_anchor(anchor_id, label='')`
次に追加するセクションの手前にアンカーを置き、ナビ項目として登録する。
`label` を省略するとアンカーだけ作られ、ナビには出ない。
**`add_summary` / `add_table` など継承メソッドをナビに載せる唯一の方法。**

各インタラクティブメソッドの `anchor=` 引数は `('id', 'ラベル')` タプル、
または ID 文字列だけを受け取る（内部で `add_anchor` を呼ぶ）。

### `add_accordion(title, items, anchor=None, filters=None, search_placeholder='', note='')`

| items のキー | 型 | 説明 |
|---|---|---|
| `id` | str | アンカー ID。タイムラインの `jump` 先。省略時は自動採番 |
| `name` | str | 見出し（太字・紺） |
| `badges` | list | `[{'text','color'}]` color は `navy` / `green` / `amber` / `red` |
| `meta` | str | 見出し右の説明テキスト（可変幅） |
| `right` | str | 右端の強調テキスト（日付・金額など。赤朱色・等幅数字） |
| `accent` | bool | True で左ボーダーを赤朱色に |
| `filters` | list | フィルターチップのキー（複数可） |
| `search` | str | 検索対象テキスト。省略時は本文から自動生成 |
| `columns` | list | `[{'title','body'}]` を 2 カラムで先に描画 |
| `blocks` | list | `[{'title','body','impact','html'}]` `impact=True` で赤朱色の左線ボックス |
| `tags` | list | 緑タグの一覧 |
| `links` | list | `[{'cat','label','url'}]` 出典リンク |

`filters` 引数は `[{'label': 表示名, 'key': 絞り込みキー, 'hl': bool}]`。
「すべて」チップは自動で先頭に付く。検索と AND 条件で効く。

`body` は自動で HTML エスケープされる。HTML を入れたい場合だけ `html` キーを使う
（その場合エスケープされないので、外部由来のテキストを入れてはならない）。

### `add_timeline(title, rows, anchor=None)`
`rows`: `[{'date','text','jump','accent'}]`
`jump` にアコーディオン item の `id` を渡すと、クリックでその項目が開いてスクロールする。
`accent=True` でノードが赤朱色＋グロー。

### `add_tabs(title, tabs, anchor=None)`
`tabs`: `[{'label','html'}]`。`html` は自己完結した HTML 断片。
先頭タブが初期表示。タブ切替のたびにそのパネル内の棒グラフが再アニメーションする。
複数のタブセクションを置いても `data-group` で独立して動く。

### `bar_chart(rows)` / `add_bar_chart(title, rows, anchor=None, lead='')`
`rows`: `[{'label','value'(0-100),'display','hl','note'}]`
`bar_chart` は HTML 断片を返す静的メソッド（タブやカードに流し込む用）、
`add_bar_chart` はセクションとして追加する。
`display` を指定すると数値の代わりに任意ラベル（例「追い風 強」）を出せる。

### `bubble_chart(rows, x_label='X', y_label='Y')` / `add_bubble_chart(...)`

`rows`: `[{'label','x','y','size','group'}]`。2軸と円の大きさで施策ポートフォリオ等を比較する。
数値は有限値のみ受け付け、データ範囲から軸を自動調整する。`group` ごとに色分けし、各円の
`title` へ値を保持する。面積の意味は `lead` で説明する。

### `gantt_chart(rows)` / `add_gantt_chart(title, rows, anchor=None, lead='')`

`rows`: `[{'label','start','end','status','owner'}]`。日付は `YYYY-MM-DD`。
`status` は `complete` / `in-progress` / `planned` / `blocked`。開始日順に並べ、終了日が
開始日より前なら生成を中止する。依存関係やマイルストーンの詳細は表またはアコーディオンで補う。

### `map_chart(points)` / `add_map(title, points, anchor=None, lead='')`

`points`: `[{'label','lat','lng','value'}]`。緯度経度を簡略化した世界図へ配置する。
外部タイルや地理APIは呼び出さない。傾向把握専用で、境界、距離、経路、正確な位置の判断には使わない。

### `line_chart(rows, x_label='期間', y_label='値')` / `add_line_chart(...)`

`rows`: `[{'label','value','series'}]`。`label` の順序を横軸として複数系列を描く。
欠損点は接続せず、元データにない値を補間しない。系列、軸、単位を明示する。

5種類の実行例は `chart-samples.md` と `scripts/chart_samples.py` を参照する。すべてSVGまたはHTMLで
生成し、外部JavaScript、地図タイル、CDNを必要としない。

### `add_checklist(title, items, anchor=None, storage_key='gh-checklist', note='')`
`items`: `[{'text','meta'}]`。進捗バーとチェック状態は localStorage に保存される。
**`storage_key` はレポートごとに固有の文字列にすること**（既定値のままだと
別レポートとチェック状態が混ざる）。

### `add_link_list(title, links, anchor=None)`
`links`: `[{'cat','label','url'}]`。引用・出典の一覧に使う。

---

## 3. 実装ルール（守らないと壊れる）

### 3-1. 幅・高さを指定する要素には `display` を明示する
最頻出の不具合。`<span>` はインライン要素なので `width` / `height` /
上下 `margin` が無視される。棒グラフのバーが「描画されない」のはほぼこれ。

```css
/* ❌ バーが消える */
.gh-bar-fill { block-size: 100%; inline-size: 0; }

/* ✅ */
.gh-bar-fill { display: block; block-size: 100%; inline-size: 0; }
```

flex コンテナの**直下の子**は自動でブロック化されるため効くが、
その中のさらに子（トラックの中のフィル）はインラインのまま。
`gh-bar-label` / `gh-bar-val` / `gh-check-meta` / `gh-tl-date` も同じ理由で
`display: block` を明示している。

### 3-2. 高さ不定の開閉アニメーションは `grid-template-rows: 0fr → 1fr`
`max-height` を決め打ちすると内容が切れる。

```css
.gh-item-body { display: grid; grid-template-rows: 0fr; transition: grid-template-rows .28s; }
.gh-item.open .gh-item-body { grid-template-rows: 1fr; }
.gh-item-body > div { overflow: hidden; }   /* 直下の1枚が必須 */
```

### 3-3. アニメーションは必ずフォールバックを用意する
`IntersectionObserver` 非対応環境ではバーが 0% のまま残る。
`interactive_report.py` のJavaScriptは2重に保険をかけている。

1. 初期表示パネルは `setTimeout` で無条件に描画
2. `IntersectionObserver` が無い場合は全バーへ即座に最終値を代入

### 3-4. 印刷とモーション低減を必ず用意する
`@media print` でナビ・ツールバー・タブ・トップへ戻るを非表示、アコーディオンを全展開、
`.gh-panel` を全表示、バーに `print-color-adjust: exact`。
`@media (prefers-reduced-motion: reduce)` で transition を無効化。
どちらも `interactive.css` に実装済み。

### 3-5. JS はインライン、生成後に構文チェック
外部 JS は自己完結性に反するため使わない。Python の f-string で JS を組み立てると
`{` `}` のエスケープ事故が起きるため、`interactive_report.py` ではJavaScriptを
**f-string ではない生文字列 `_JS`** として保持している。生成後は必ず確認する。

```bash
python - <<'EOF' > /tmp/check.js
h = open('working/report.html').read()
print(h.split('<script>')[1].split('</script>')[0])
EOF
node --check /tmp/check.js
```

### 3-6. CSS クラスの定義漏れを機械的に確認する
```python
import re
h = open('working/report.html').read()
css = h.split('<style>')[1].split('</style>')[0]
used = {c for m in re.finditer(r'class="([^"]+)"', h)
          for c in m.group(1).split() if c.startswith('gh-')}
print([c for c in sorted(used) if '.' + c not in css])   # → [] であること
```

### 3-7. アクセシビリティ
- 開閉ヘッダーは `role="button"` `tabindex="0"` `aria-expanded` を持たせる（実装済み）
- Enter / Space でも開閉できる（実装済み）
- 色だけで情報を伝えない。バッジ・タグには必ずテキストを入れる

---

## 4. 生成後チェックリスト

- [ ] HTMLとJavaScriptの構文エラーがない
- [ ] `node --check` で JS 構文 OK
- [ ] CSS クラスの定義漏れが `[]`
- [ ] 棒グラフ・プログレスバーが実際に伸びる（`display` 明示の確認）
- [ ] バブル、ガント、地図、棒、折れ線の点数・期間・最小値・最大値が入力と一致する
- [ ] 軸、単位、系列、概略地図の制約をテキストでも確認できる
- [ ] タブを切り替えても中身が表示される
- [ ] チェックリストの `storage_key` がレポート固有になっている
- [ ] `output/` へは `CopyArtifact` で発行（`output/` は読み取り専用）
