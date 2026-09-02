# Interactive Report コンポーネントガイド

すべてのコンポーネントは `report.css` のCSSクラスを使用する。

---

## ページヘッダー

```html
<header class="gh-header">
  <div class="gh-header-label">PREMIUM</div>        <!-- 金バッジ（任意） -->
  <h1 class="gh-header-title">株式会社〇〇 年次レポート</h1>
  <p class="gh-header-meta">2026年6月　｜　東京都〇〇区</p>

  <!-- 統計ストリップ（任意） -->
  <div class="gh-header-stats">
    <div class="gh-header-stat"><div class="v">99.5%</div><div class="l">稼働率</div></div>
    <div class="gh-header-stat"><div class="v">4.5</div><div class="l">満足度</div></div>
  </div>
</header>
```

---

## KPI カードグリッド

```html
<div class="gh-section">
  <div class="gh-section-title">主要 KPI ハイライト</div>
  <div class="gh-kpi-grid">

    <!-- 左ボーダーなし（デフォルト紺） -->
    <div class="gh-kpi-card">
      <div class="gh-kpi-label">稼働率</div>
      <div class="gh-kpi-value">99.5<span class="gh-kpi-unit">%</span></div>
      <div class="gh-kpi-delta good">▲ +0.3pt</div>
      <span class="gh-kpi-prev">前年 99.2%</span>
    </div>

    <!-- 緑ボーダー -->
    <div class="gh-kpi-card green">
      <div class="gh-kpi-label">ダウンタイム削減</div>
      <div class="gh-kpi-value">▼50<span class="gh-kpi-unit">%</span></div>
      <div class="gh-kpi-delta good">18.5h → 9.2h</div>
    </div>

    <!-- ハイライト（赤朱色）ボーダー — 緊急・要注意 -->
    <div class="gh-kpi-card hl">
      <div class="gh-kpi-label">要更新機器</div>
      <div class="gh-kpi-value">1<span class="gh-kpi-unit">台</span></div>
      <div class="gh-kpi-delta bad">保守終了 6ヶ月以内</div>
    </div>

  </div>
</div>
```

**左ボーダー色クラス**: `green` / `amber` / `red` / `hl`（赤朱色）/ デフォルト（紺）
**デルタクラス**: `good`（緑）/ `warn`（黄）/ `bad`（赤）

---

## コンテンツカードグリッド

```html
<div class="gh-section">
  <div class="gh-section-title">改善提案</div>

  <!-- 3 カラム -->
  <div class="gh-card-grid cols-3">
    <div class="gh-card">
      <!-- 利用可能な画像は検証してbase64で埋め込む -->
      <img class="gh-card-icon" src="data:image/png;base64,..." alt="copilot">
      <div class="gh-card-title">MFP-004 更新（保守終了間近）</div>
      <div class="gh-card-body">
        MFP-004 は導入から約 8 年、保守終了まで残り約 6 ヶ月。
        後継モデルへの更新候補を比較します。
      </div>
      <!-- 効果ボックス（任意） -->
      <div class="gh-card-effect">ダウンタイム ▼50%、消費電力 ▼25%</div>
    </div>
    <div class="gh-card">...</div>
    <div class="gh-card">...</div>
  </div>
</div>
```

**グリッドクラス**: `cols-2` / `cols-3` / `cols-4`

---

## データテーブル

```html
<div class="gh-section">
  <div class="gh-section-title">年間保守実績 — 対前年比較</div>
  <div class="gh-table-wrap">
    <table class="gh-table">
      <thead>
        <tr>
          <th>KPI</th>
          <th style="text-align:end">2025年度</th>
          <th style="text-align:end">2026年度</th>
          <th style="text-align:end">変化</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>コール件数</td>
          <td class="num">78 件</td>
          <td class="num imp">41 件</td>         <!-- imp = 太字 -->
          <td class="num ok">▼ 47.4%</td>        <!-- ok = 緑 -->
        </tr>
        <tr>
          <td>稼働率</td>
          <td class="num">99.2%</td>
          <td class="num imp">99.5%</td>
          <td class="num ok">▲ +0.3pt</td>
        </tr>
        <tr>
          <td>要更新機器</td>
          <td class="num">0 台</td>
          <td class="num imp hl">1 台</td>        <!-- hl = 赤朱色強調 -->
          <td class="num warn">▲ +1</td>          <!-- warn = 黄 -->
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

**セルクラス**: `num`（右寄せ）/ `imp`（太字）/ `hl`（赤朱色）/ `ok`（緑）/ `warn`（黄）

---

## ステータスバッジ（テーブル・カード内）

```html
<span class="gh-badge red">  <span class="gh-badge-dot"></span> 更新推奨 </span>
<span class="gh-badge amber"><span class="gh-badge-dot"></span> 更新検討 </span>
<span class="gh-badge green"><span class="gh-badge-dot"></span> 継続利用 </span>
<span class="gh-badge navy"> <span class="gh-badge-dot"></span> Premium   </span>
```

---

## セクション区切り（ダーク背景）

```html
<!-- 背景画像あり（CSS 変数で埋め込み） -->
<div class="gh-divider"
     style="--gh-div-bg-img:url('data:image/png;base64,...')">
  <div class="gh-divider-title">機器ライフサイクル</div>
  <p class="gh-divider-sub">全 5 台の状況と更新計画</p>
</div>

<!-- 背景画像なし -->
<div class="gh-divider">
  <div class="gh-divider-title">セクション名</div>
</div>
```

---

## エグゼクティブサマリーボックス

```html
<div class="gh-section">
  <div class="gh-summary">
    <div class="gh-summary-title">エグゼクティブサマリ</div>
    <p>
      2026年度の稼働率は <span class="gh-navy-txt">99.5%</span>、
      ダウンタイムは前年比 <span class="gh-hl">▼50%</span> 改善しました。
      一方、<strong>MFP-004 の保守終了まで残り約 6 ヶ月</strong>であり、
      早急な更新判断が必要です。
    </p>
  </div>
</div>
```

---

## アクションリスト

```html
<div class="gh-section">
  <div class="gh-section-title">次のアクション</div>
  <div class="gh-action-list">

    <div class="gh-action-item">
      <div class="gh-action-num">1</div>
      <div class="gh-action-text"><strong>MFP-004 更新の発注可否をご決裁いただく</strong></div>
      <span class="gh-action-owner">御社担当者様</span>
      <span class="gh-action-date">2026年9月末まで</span>
    </div>

    <div class="gh-action-item">
      <div class="gh-action-num">2</div>
      <div class="gh-action-text">カラー集約の運用ルール案を提示する</div>
      <span class="gh-action-owner">弊社</span>
      <span class="gh-action-date">2026年8月</span>
    </div>

  </div>
</div>
```

---

## プログレスバー（残存年数など）

```html
<!-- 赤: 緊急 -->
<div class="gh-progress">
  <div class="gh-progress-fill red" style="width:12%"></div>
</div>

<!-- 黄: 要注意 -->
<div class="gh-progress">
  <div class="gh-progress-fill amber" style="width:37%"></div>
</div>

<!-- 緑: 良好 -->
<div class="gh-progress">
  <div class="gh-progress-fill green" style="width:75%"></div>
</div>
```

---

## インラインテキストヘルパー

```html
<p>
  稼働率は <span class="gh-hl">過去最高</span>を記録。
  保守コストは <span class="gh-navy-txt">前年比 47%削減</span>。
  <span class="gh-muted">（参考：前年度コール件数 78 件）</span>
</p>
```
