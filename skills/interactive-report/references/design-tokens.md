# Interactive Report CSS変数リファレンス

すべての変数は `:root` で定義。`@media (prefers-color-scheme: dark)` で上書き。

## Colors

| CSS 変数 | Light | Dark | 用途 |
|---|---|---|---|
| `--gh-navy` | `#1B3A6B` | `#4A90D9` | 基調色・カードタイトル・セクションタイトル |
| `--gh-navy-dark` | `#122952` | `#6AABE8` | ページタイトル・強調 |
| `--gh-navy-light` | `#2A5298` | `#5A9FD4` | セカンダリアクセント |
| `--gh-hl` | `#C83F2C` | `#E8604A` | ハイライト（赤朱色） |
| `--gh-hl-alt` | `#D4502D` | `#F07055` | ハイライトバリアント |
| `--gh-bg` | `#EBF2FC` | `#0C1929` | ページ背景 |
| `--gh-card-bg` | `#FFFFFF` | `#152135` | カード背景 |
| `--gh-card-bg2` | `#F5F9FE` | `#1C2D42` | テーブルストライプ行 |
| `--gh-dark-bg` | `#0D1117` | `#060C14` | セクション区切り背景 |
| `--gh-text` | `#1A2A3A` | `#E3EDF7` | 本文テキスト |
| `--gh-text-muted` | `#607D8B` | `#7A9BB5` | サブテキスト |
| `--gh-text-white` | `#FFFFFF` | `#FFFFFF` | ダーク背景上のテキスト |
| `--gh-border` | `#C8D9EF` | `#243548` | カード枠線 |
| `--gh-border-lt` | `#DCE9F8` | `#1C2D42` | 薄い区切り線 |
| `--gh-green` | `#2E7D32` | `#81C784` | 良好・改善を示す緑 |
| `--gh-green-bg` | `#E8F5E9` | `#1A3320` | 緑バッジ背景 |
| `--gh-amber` | `#B45309` | `#FBBF24` | 警告・要注意の黄 |
| `--gh-amber-bg` | `#FFFBEB` | `#2E1800` | 黄バッジ背景 |
| `--gh-red` | `#991B1B` | `#FCA5A5` | 危険・問題の赤 |
| `--gh-red-bg` | `#FEF2F2` | `#3B0D0D` | 赤バッジ背景 |

## Typography

| CSS 変数 | 値 | 用途 |
|---|---|---|
| `--gh-font` | 'Yu Gothic UI', 'Yu Gothic', ... | 全要素のフォントスタック |

**Font sizes（直接変数なし — 各コンポーネント内で固定値を使用）**:

| 要素 | サイズ | ウェイト |
|---|---|---|
| `.gh-header-title` | 24px | 700 |
| `.gh-divider-title` | 22px | 700 |
| `.gh-card-title` | 15px | 700 |
| `.gh-kpi-value` | 28px | 700 |
| `.gh-section-title` | 10px | 800 (大文字) |
| `.gh-table th` | 10px | 700 (大文字) |
| `.gh-table td`, `.gh-card-body` | 13px | 400 |
| body | **14px** | 400（最小サイズ） |
| `.gh-action-owner`, `.gh-action-date`, `.gh-kpi-label` | 10–11px | 600–700 |
| `.gh-footer` | 11px | 400 |

## Dimensions

| CSS 変数 | 値 | 用途 |
|---|---|---|
| `--gh-radius` | `10px` | カード・ラッパーの丸角 |
| `--gh-radius-sm` | `6px` | バッジ・小要素の丸角 |
| `--gh-shadow` | 0 2px 8px ... | カードの影 |
| `--gh-gap` | `12px` | グリッド間隔 |
| `--gh-max-w` | `1080px` | コンテンツ最大幅 |

## セクション区切りの背景画像

`.gh-divider` は CSS 変数 `--gh-div-bg-img` に base64 URL を渡すと背景画像を表示:

```html
<div class="gh-divider"
     style="--gh-div-bg-img:url('data:image/png;base64,...')">
  <div class="gh-divider-title">セクション名</div>
</div>
```

`report.py` の `add_divider(bg_image='images/background.png')` で自動的に埋め込まれる。

背景画像は `70%` のオーバーレイで暗くされるため、コントラストは担保される。
