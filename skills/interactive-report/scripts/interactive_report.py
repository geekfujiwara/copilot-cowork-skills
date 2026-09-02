# -*- coding: utf-8 -*-
"""
interactive_report.py — interactive-report extension

Report（report.py）を継承し、以下のインタラクティブ部品を追加する。
生成物は依然として「完全自己完結型 HTML」（外部 CSS/JS/画像なし）。

  add_nav_item / set_nav_buttons  スティッキーナビ（スクロール連動ハイライト）
  add_anchor                      既存セクションにアンカー＋ナビ項目を付与
  add_accordion                   検索・フィルター付き 開閉カードリスト
  add_timeline                    縦型タイムライン（クリックでアコーディオンへジャンプ）
  add_tabs                        タブ切替パネル
  add_bar_chart                   横棒グラフ（スクロールで伸びるアニメーション）
  add_bubble_chart                優先度・ポートフォリオ用バブルチャート
  add_gantt_chart                 期間・進捗用ガントチャート
  add_map                         緯度経度に基づく概略地図
  add_line_chart                  時系列比較用折れ線グラフ
  add_checklist                   進捗バー付きチェックリスト（localStorage 保存）
  add_link_list                   引用・出典リンク一覧

使い方:
    import sys
    sys.path.insert(0, str(Path('scripts').resolve()))
    from interactive_report import InteractiveReport

    r = InteractiveReport('タイトル', subtitle='サブ', label='REPORT', date='<対象日>')
    r.set_header_stats([...])
    r.add_anchor('summary', 'サマリ'); r.add_summary('サマリ', '本文…')
    r.add_accordion('顧客一覧', items=[...], anchor=('list', '一覧'))
    r.save('working/report.html')      # → output/ へは CopyArtifact で発行

設計上の必須ルール:
  幅・高さを指定する要素には必ず display を明示する。<span> のままでは
  インライン要素として扱われ width/height が無視され、棒グラフが消える。
"""

import json
import math
from datetime import date
from urllib.parse import urlparse
from report import Report, _e, _CSS_FILE, _INT_CSS_FILE   # noqa: F401


# ── JavaScript（テンプレート。{} は使わず % 置換で埋め込む） ──────────
_JS = r"""
(function () {
  'use strict';
  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- スクロール出現アニメーション対象を自動付与 ---- */
  $$('.gh-main > .gh-section').forEach(function (el) { el.classList.add('gh-reveal'); });

  /* ---- アコーディオン ---- */
  var items = $$('.gh-item');
  function toggle(item, force) {
    var open = (typeof force === 'boolean')
      ? item.classList.toggle('open', force)
      : item.classList.toggle('open');
    var head = $('.gh-item-head', item);
    if (head) head.setAttribute('aria-expanded', open ? 'true' : 'false');
    return open;
  }
  items.forEach(function (item) {
    var head = $('.gh-item-head', item);
    if (!head) return;
    head.addEventListener('click', function () { toggle(item); });
    head.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(item); }
    });
  });

  $$('[data-expand-all]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var visible = items.filter(function (i) { return !i.classList.contains('hidden'); });
      var anyClosed = visible.some(function (i) { return !i.classList.contains('open'); });
      visible.forEach(function (i) { toggle(i, anyClosed); });
      btn.textContent = anyClosed ? 'すべて閉じる' : 'すべて展開';
    });
  });

  /* ---- 検索 + フィルターチップ（アコーディオン単位） ---- */
  $$('.gh-acc').forEach(function (acc) {
    var scope   = acc.closest('.gh-section') || document;
    var rows    = $$('.gh-item', acc);
    var chips   = $$('.gh-chip', scope);
    var input   = $('.gh-search', scope);
    var countEl = $('.gh-count', scope);
    var emptyEl = $('.gh-empty', scope);
    var filter = 'all', query = '';

    function apply() {
      var shown = 0;
      rows.forEach(function (i) {
        var tags = (i.dataset.filters || '').split('|');
        var okF  = (filter === 'all') || tags.indexOf(filter) >= 0;
        var okQ  = !query || (i.dataset.search || '').toLowerCase().indexOf(query) >= 0;
        var ok   = okF && okQ;
        i.classList.toggle('hidden', !ok);
        if (ok) shown++;
      });
      if (countEl) countEl.textContent = shown + ' / ' + rows.length + ' 件を表示';
      if (emptyEl) emptyEl.classList.toggle('on', shown === 0);
    }
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.classList.remove('on'); });
        chip.classList.add('on');
        filter = chip.dataset.f;
        apply();
      });
    });
    if (input) input.addEventListener('input', function (e) {
      query = e.target.value.trim().toLowerCase();
      apply();
    });
    apply();
  });

  /* ---- 横棒グラフのアニメーション ---- */
  function animateBars(root) {
    if (!root) return;
    $$('.gh-bar-fill', root).forEach(function (b, idx) {
      b.style.width = '0%';
      setTimeout(function () { b.style.width = b.dataset.w + '%'; }, 60 + idx * 55);
    });
  }
  /* 初期表示パネルは無条件に描画（IntersectionObserver 非対応でも必ず出す） */
  setTimeout(function () { $$('.gh-panel.on').forEach(animateBars); }, 200);

  /* ---- タブ ---- */
  $$('.gh-tabs').forEach(function (bar) {
    var group = bar.dataset.group;
    var tabs  = $$('.gh-tab', bar);
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.classList.remove('on'); });
        $$('.gh-panel[data-group="' + group + '"]').forEach(function (p) { p.classList.remove('on'); });
        tab.classList.add('on');
        var panel = document.getElementById(tab.dataset.tab);
        if (panel) { panel.classList.add('on'); animateBars(panel); }
      });
    });
  });

  /* ---- タイムライン → アコーディオンへジャンプ ---- */
  $$('.gh-tl-row[data-jump]').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function () {
      var target = document.getElementById(row.dataset.jump);
      if (!target) return;
      target.classList.remove('hidden');
      toggle(target, true);
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });

  /* ---- チェックリスト（localStorage 保存） ---- */
  $$('.gh-checklist').forEach(function (list) {
    var key   = list.dataset.key || 'gh-checklist';
    var boxes = $$('input[type=checkbox]', list);
    var fill  = $('.gh-progress-fill', list);
    var label = $('.gh-progress-label', list);
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) { saved = {}; }

    function refresh() {
      var done = boxes.filter(function (b) { return b.checked; }).length;
      if (fill)  fill.style.width = (boxes.length ? (done / boxes.length * 100) : 0) + '%';
      if (label) label.textContent = done + ' / ' + boxes.length + ' 件 完了';
    }
    boxes.forEach(function (b) {
      if (saved[b.dataset.k]) { b.checked = true; b.closest('.gh-check').classList.add('done'); }
      b.addEventListener('change', function () {
        b.closest('.gh-check').classList.toggle('done', b.checked);
        saved[b.dataset.k] = b.checked;
        try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
        refresh();
      });
    });
    refresh();
  });

  /* ---- スクロール連動（出現 / ナビ / トップへ戻る） ---- */
  if (!('IntersectionObserver' in window)) {
    $$('.gh-reveal').forEach(function (el) { el.classList.add('in'); });
    $$('.gh-bar-fill').forEach(function (b) { b.style.width = b.dataset.w + '%'; });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        animateBars(en.target);
        io.unobserve(en.target);
      });
    }, { threshold: 0.08 });
    $$('.gh-reveal').forEach(function (el) { io.observe(el); });
  }

  var links  = $$('.gh-nav a');
  var toTop  = $('.gh-totop');
  var anchors = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function onScroll() {
    var y = window.scrollY + 130, cur = -1;
    anchors.forEach(function (el, i) { if (el && el.offsetTop <= y) cur = i; });
    links.forEach(function (a, i) { a.classList.toggle('active', i === cur); });
    if (toTop) toTop.classList.toggle('show', window.scrollY > 500);
  }
  if (links.length) { window.addEventListener('scroll', onScroll, { passive: true }); onScroll(); }
  if (toTop) toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  $$('[data-print]').forEach(function (btn) {
    btn.addEventListener('click', function () { window.print(); });
  });
})();
"""


class InteractiveReport(Report):
    """Report にインタラクティブ部品を足したレポートビルダー。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nav = []           # [(anchor_id, label)]
        self._nav_buttons = []   # [{'label','action'}]
        self._tab_seq = 0
        self._show_totop = True

    # ── ナビゲーション ──────────────────────────────────
    def set_nav_buttons(self, expand_all: bool = True, print_button: bool = True):
        """ナビ右端のボタン（すべて展開 / 印刷）を設定する。"""
        self._nav_buttons = []
        if expand_all:
            self._nav_buttons.append({'label': 'すべて展開', 'attr': 'data-expand-all'})
        if print_button:
            self._nav_buttons.append({'label': '印刷', 'attr': 'data-print'})
        return self

    def add_anchor(self, anchor_id: str, label: str = ''):
        """次のセクションの手前にアンカーを置き、ナビ項目として登録する。

        add_summary / add_table など Report 由来のセクションにも
        この呼び出しでナビからジャンプできるようになる。
        """
        self.add_raw(f'<span class="gh-anchor" id="{_e(anchor_id)}"></span>')
        if label:
            self._nav.append((anchor_id, label))
        return self

    def _anchor(self, anchor):
        """anchor 引数（'id' か ('id','label')）を処理してアンカーを出力。"""
        if not anchor:
            return
        if isinstance(anchor, (tuple, list)):
            self.add_anchor(anchor[0], anchor[1] if len(anchor) > 1 else '')
        else:
            self.add_anchor(anchor)

    # ── アコーディオン ──────────────────────────────────
    def add_accordion(self, title: str, items: list, anchor=None,
                      filters: list = None, search_placeholder: str = '',
                      note: str = ''):
        """検索・フィルター付きの開閉カードリスト。

        items（1 件 = 1 カード）:
          id       str   — アンカー ID（タイムラインの jump 先。省略時は自動採番）
          name     str   — 見出し（太字・紺）
          badges   list  — [{'text': str, 'color': 'navy'|'green'|'amber'|'red'}]
          meta     str   — 見出し右の説明テキスト
          right    str   — 右端の強調テキスト（日付・金額など）
          accent   bool  — True で左ボーダーを赤朱色に
          filters  list  — フィルターチップで絞り込む際のキー（例 ['新規','高']）
          search   str   — 検索対象テキスト（省略時は本文から自動生成）
          blocks   list  — [{'title': str, 'body': str, 'impact': bool, 'html': str}]
          columns  list  — [{'title','body'}] を 2 カラムで並べる（blocks より前に描画）
          tags     list  — 緑タグの一覧（新しい機会・キーワードなど）
          links    list  — [{'label': str, 'url': str, 'cat': str}] 出典リンク
        filters: [{'label': str, 'key': str, 'hl': bool}] — 'すべて' は自動で先頭に付く
        """
        self._anchor(anchor)
        self._sections.append({
            'type': 'accordion', 'title': title, 'items': items,
            'filters': filters or [], 'ph': search_placeholder, 'note': note,
        })
        return self

    # ── タイムライン ────────────────────────────────────
    def add_timeline(self, title: str, rows: list, anchor=None):
        """縦型タイムライン。

        rows: [{'date': str, 'text': str, 'jump': 'item-id', 'accent': bool}]
              jump を指定すると、クリックで該当アコーディオンが開いてスクロールする。
        """
        self._anchor(anchor)
        self._sections.append({'type': 'timeline', 'title': title, 'rows': rows})
        return self

    # ── タブ ────────────────────────────────────────────
    def add_tabs(self, title: str, tabs: list, anchor=None):
        """タブ切替パネル。

        tabs: [{'label': str, 'html': str}]  html は自己完結した HTML 断片。
              bar_chart() / table_html() の戻り値をそのまま入れられる。
        """
        self._anchor(anchor)
        self._tab_seq += 1
        self._sections.append({'type': 'tabs', 'title': title,
                               'tabs': tabs, 'group': f'g{self._tab_seq}'})
        return self

    # ── 横棒グラフ ──────────────────────────────────────
    @staticmethod
    def bar_chart(rows: list) -> str:
        """横棒グラフの HTML 断片を返す（add_tabs の html に流し込める）。

        rows: [{'label': str, 'value': 0-100, 'display': str, 'hl': bool, 'note': str}]
              display 省略時は「値 / 100」表記。
        """
        out = []
        for r in rows:
            v = max(0, min(100, float(r.get('value', 0))))
            disp = r.get('display') or f'{r.get("value")} / 100'
            hl = ' hl' if r.get('hl') else ''
            out.append(
                '<div class="gh-bar-row">'
                f'<span class="gh-bar-label">{_e(r.get("label",""))}</span>'
                '<span class="gh-bar-track">'
                f'<span class="gh-bar-fill{hl}" data-w="{v:g}"></span></span>'
                f'<span class="gh-bar-val">{_e(disp)}</span></div>'
            )
            if r.get('note'):
                out.append(f'<div class="gh-bar-note">{_e(r["note"])}</div>')
        return ('<div class="gh-bar-chart" role="img" aria-label="カテゴリ比較の棒グラフ">'
          + ''.join(out) + '</div>')

    def add_bar_chart(self, title: str, rows: list, anchor=None, lead: str = ''):
        """横棒グラフを単独セクションとして追加する。"""
        self._anchor(anchor)
        lead_h = f'<div class="gh-card-body" style="margin-block-end:10px">{_e(lead)}</div>' if lead else ''
        self.add_raw(
            f'<div class="gh-section"><div class="gh-section-title">{_e(title)}</div>'
            f'<div class="gh-card">{lead_h}{self.bar_chart(rows)}</div></div>')
        return self

    @staticmethod
    def _number(value, field: str) -> float:
      """有限の数値だけをチャート座標として受け取る。"""
      try:
        number = float(value)
      except (TypeError, ValueError) as exc:
        raise ValueError(f'{field} must be a number') from exc
      if not math.isfinite(number):
        raise ValueError(f'{field} must be finite')
      return number

    @staticmethod
    def _range(values: list[float]) -> tuple[float, float]:
      low, high = min(values), max(values)
      if low == high:
        return low - 0.5, high + 0.5
      return low, high

    @staticmethod
    def _chart_card(title: str, chart: str, lead: str = '') -> str:
      lead_html = (f'<p class="gh-chart-lead">{_e(lead)}</p>' if lead else '')
      return (f'<div class="gh-section"><div class="gh-section-title">{_e(title)}</div>'
          f'<div class="gh-card gh-chart-card">{lead_html}{chart}</div></div>')

    @classmethod
    def bubble_chart(cls, rows: list, x_label: str = 'X', y_label: str = 'Y') -> str:
      """バブルチャートのSVG断片を返す。

      rows: [{'label', 'x', 'y', 'size', 'group'}]
      """
      if not rows:
        raise ValueError('bubble chart requires at least one row')
      points = [(row, cls._number(row.get('x'), 'x'),
             cls._number(row.get('y'), 'y'),
             max(0.0, cls._number(row.get('size', 1), 'size')))
            for row in rows]
      x_min, x_max = cls._range([point[1] for point in points])
      y_min, y_max = cls._range([point[2] for point in points])
      size_max = max(point[3] for point in points) or 1.0
      colors = ('#1B3A6B', '#2E7D32', '#B45309', '#C83F2C', '#6B4FA1')
      groups: dict[str, str] = {}
      bubbles = []
      for row, x_value, y_value, size in points:
        group = str(row.get('group', ''))
        if group not in groups:
          groups[group] = colors[len(groups) % len(colors)]
        x = 76 + (x_value - x_min) / (x_max - x_min) * 780
        y = 350 - (y_value - y_min) / (y_max - y_min) * 310
        radius = 8 + math.sqrt(size / size_max) * 24
        title = (f'{row.get("label", "")}: {x_label} {x_value:g}, '
             f'{y_label} {y_value:g}, size {size:g}')
        bubbles.append(
          f'<g class="gh-bubble" tabindex="0"><title>{_e(title)}</title>'
          f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" '
          f'fill="{groups[group]}" fill-opacity=".74" />'
          f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle">'
          f'{_e(row.get("label", ""))}</text></g>')
      legend = ''.join(
        f'<span><i style="background:{color}"></i>{_e(group or "その他")}</span>'
        for group, color in groups.items())
      return (
        f'<div class="gh-chart-legend">{legend}</div>'
            f'<svg class="gh-chart gh-bubble-chart" viewBox="0 0 900 400" role="img" '
        f'aria-label="{_e(x_label)}と{_e(y_label)}のバブルチャート">'
        '<line class="gh-axis" x1="76" y1="350" x2="856" y2="350" />'
        '<line class="gh-axis" x1="76" y1="40" x2="76" y2="350" />'
        f'<text class="gh-axis-label" x="466" y="390">{_e(x_label)}</text>'
        f'<text class="gh-axis-label" transform="translate(18 195) rotate(-90)">{_e(y_label)}</text>'
        f'<text class="gh-tick" x="76" y="370">{x_min:g}</text>'
        f'<text class="gh-tick" x="856" y="370" text-anchor="end">{x_max:g}</text>'
        f'<text class="gh-tick" x="66" y="350" text-anchor="end">{y_min:g}</text>'
        f'<text class="gh-tick" x="66" y="44" text-anchor="end">{y_max:g}</text>'
        f'{"".join(bubbles)}</svg>')

    def add_bubble_chart(self, title: str, rows: list, anchor=None, lead: str = '',
               x_label: str = 'X', y_label: str = 'Y'):
      self._anchor(anchor)
      self.add_raw(self._chart_card(title, self.bubble_chart(rows, x_label, y_label), lead))
      return self

    @classmethod
    def gantt_chart(cls, rows: list) -> str:
      """ガントチャートのSVG断片を返す。

      rows: [{'label', 'start', 'end', 'status', 'owner'}]
      """
      if not rows:
        raise ValueError('gantt chart requires at least one row')
      tasks = []
      for row in rows:
        try:
          start, end = date.fromisoformat(str(row.get('start'))), date.fromisoformat(str(row.get('end')))
        except ValueError as exc:
          raise ValueError('start and end must use YYYY-MM-DD') from exc
        if end < start:
          raise ValueError('gantt end must not precede start')
        tasks.append((row, start, end))
      tasks.sort(key=lambda item: (item[1], item[2]))
      first = min(item[1] for item in tasks)
      last = max(item[2] for item in tasks)
      span = max(1, (last - first).days + 1)
      height = 64 + len(tasks) * 46
      colors = {'complete': '#2E7D32', 'in-progress': '#B45309',
            'planned': '#1B3A6B', 'blocked': '#C83F2C'}
      task_svg = []
      for index, (row, start, end) in enumerate(tasks):
        y = 48 + index * 46
        x = 220 + (start - first).days / span * 640
        width = max(5, ((end - start).days + 1) / span * 640)
        status = str(row.get('status', 'planned'))
        color = colors.get(status, colors['planned'])
        detail = f'{row.get("label", "")}: {start.isoformat()}–{end.isoformat()}, {status}'
        task_svg.append(
          f'<text class="gh-gantt-label" x="8" y="{y + 18}">{_e(row.get("label", ""))}</text>'
          f'<g class="gh-gantt-task" tabindex="0"><title>{_e(detail)}</title>'
          f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="26" rx="5" fill="{color}" />'
          f'<text class="gh-gantt-owner" x="{x + 6:.1f}" y="{y + 18}">{_e(row.get("owner", ""))}</text></g>')
      return (
            f'<svg class="gh-chart gh-gantt-chart" viewBox="0 0 900 {height}" role="img" '
        f'aria-label="{first.isoformat()}から{last.isoformat()}までのガントチャート">'
        f'<text class="gh-tick" x="220" y="24">{first.isoformat()}</text>'
        f'<text class="gh-tick" x="860" y="24" text-anchor="end">{last.isoformat()}</text>'
        f'<line class="gh-axis" x1="220" y1="34" x2="860" y2="34" />'
        f'{"".join(task_svg)}</svg>')

    def add_gantt_chart(self, title: str, rows: list, anchor=None, lead: str = ''):
      self._anchor(anchor)
      self.add_raw(self._chart_card(title, self.gantt_chart(rows), lead))
      return self

    @classmethod
    def map_chart(cls, points: list) -> str:
      """緯度経度を等距円筒図法で配置した概略地図SVGを返す。"""
      if not points:
        raise ValueError('map requires at least one point')
      markers = []
      for point in points:
        lat = max(-90.0, min(90.0, cls._number(point.get('lat'), 'lat')))
        lng = max(-180.0, min(180.0, cls._number(point.get('lng'), 'lng')))
        x = 30 + (lng + 180) / 360 * 840
        y = 30 + (90 - lat) / 180 * 360
        detail = f'{point.get("label", "")}: {point.get("value", "")}, {lat:g}, {lng:g}'
        markers.append(
          f'<g class="gh-map-marker" tabindex="0"><title>{_e(detail)}</title>'
          f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" />'
          f'<text x="{x + 12:.1f}" y="{y + 4:.1f}">{_e(point.get("label", ""))} '
          f'{_e(point.get("value", ""))}</text></g>')
      return (
            '<svg class="gh-chart gh-map-chart" viewBox="0 0 900 420" role="img" '
        'aria-label="地点の分布を示す概略地図。境界線は正確な地理情報ではありません">'
        '<rect class="gh-map-water" x="20" y="20" width="860" height="380" rx="8" />'
        '<path class="gh-map-land" d="M80 105 L165 65 245 92 220 150 155 170 105 145 Z '
        'M210 180 L265 195 290 270 250 350 220 300 Z '
        'M390 85 L480 55 560 80 625 70 720 105 790 155 745 205 665 195 615 250 '
        '555 220 510 145 445 135 Z M690 270 L770 285 790 340 720 365 675 325 Z" />'
        '<g class="gh-map-grid"><path d="M20 115H880 M20 210H880 M20 305H880 '
        'M235 20V400 M450 20V400 M665 20V400" /></g>'
        f'{"".join(markers)}</svg><p class="gh-chart-note">概略表示です。境界・距離・位置の正確性を要する用途には使用しません。</p>')

    def add_map(self, title: str, points: list, anchor=None, lead: str = ''):
      self._anchor(anchor)
      self.add_raw(self._chart_card(title, self.map_chart(points), lead))
      return self

    @classmethod
    def line_chart(cls, rows: list, x_label: str = '期間', y_label: str = '値') -> str:
      """複数系列の折れ線グラフSVGを返す。

      rows: [{'label', 'value', 'series'}]
      """
      if not rows:
        raise ValueError('line chart requires at least one row')
      labels = list(dict.fromkeys(str(row.get('label', '')) for row in rows))
      series: dict[str, dict[str, float]] = {}
      for row in rows:
        name = str(row.get('series', '値'))
        series.setdefault(name, {})[str(row.get('label', ''))] = cls._number(row.get('value'), 'value')
      values = [value for points in series.values() for value in points.values()]
      y_min, y_max = cls._range(values)
      colors = ('#1B3A6B', '#C83F2C', '#2E7D32', '#B45309', '#6B4FA1')
      lines, legend = [], []
      for index, (name, points) in enumerate(series.items()):
        color = colors[index % len(colors)]
        segments = []
        coords = []
        dots = []
        for label_index, label in enumerate(labels):
          if label not in points:
            if coords:
              segments.append(coords)
              coords = []
            continue
          x = 76 + (label_index / max(1, len(labels) - 1)) * 780
          y = 350 - (points[label] - y_min) / (y_max - y_min) * 310
          coords.append(f'{x:.1f},{y:.1f}')
          dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4"><title>'
                f'{_e(name)} / {_e(label)}: {points[label]:g}</title></circle>')
        if coords:
          segments.append(coords)
        paths = ''.join(f'<polyline points="{" ".join(segment)}" />' for segment in segments)
        lines.append(f'<g class="gh-line-series" style="color:{color}">{paths}'
               f'{"".join(dots)}</g>')
        legend.append(f'<span><i style="background:{color}"></i>{_e(name)}</span>')
      ticks = ''.join(
        f'<text class="gh-tick" x="{76 + (i / max(1, len(labels) - 1)) * 780:.1f}" '
        f'y="372" text-anchor="middle">{_e(label)}</text>'
        for i, label in enumerate(labels))
      return (
        f'<div class="gh-chart-legend">{"".join(legend)}</div>'
            f'<svg class="gh-chart gh-line-chart" viewBox="0 0 900 400" role="img" '
        f'aria-label="{_e(x_label)}ごとの{_e(y_label)}を示す折れ線グラフ">'
        '<line class="gh-axis" x1="76" y1="350" x2="856" y2="350" />'
        '<line class="gh-axis" x1="76" y1="40" x2="76" y2="350" />'
        f'<text class="gh-axis-label" transform="translate(18 195) rotate(-90)">{_e(y_label)}</text>'
        f'<text class="gh-tick" x="66" y="350" text-anchor="end">{y_min:g}</text>'
        f'<text class="gh-tick" x="66" y="44" text-anchor="end">{y_max:g}</text>'
        f'{ticks}{"".join(lines)}</svg>')

    def add_line_chart(self, title: str, rows: list, anchor=None, lead: str = '',
               x_label: str = '期間', y_label: str = '値'):
      self._anchor(anchor)
      self.add_raw(self._chart_card(title, self.line_chart(rows, x_label, y_label), lead))
      return self

    # ── チェックリスト ──────────────────────────────────
    def add_checklist(self, title: str, items: list, anchor=None,
                      storage_key: str = 'gh-checklist', note: str = ''):
        """進捗バー付きチェックリスト。チェック状態は localStorage に保存される。

        items: [{'text': str, 'meta': str}]
        storage_key: レポートごとに固有の文字列にすること（他レポートと状態が混ざる）。
        """
        self._anchor(anchor)
        self._sections.append({'type': 'checklist', 'title': title, 'items': items,
                               'key': storage_key, 'note': note})
        return self

    # ── リンク一覧 ──────────────────────────────────────
    def add_link_list(self, title: str, links: list, anchor=None):
        """引用・出典のリンク一覧。links: [{'cat': str, 'label': str, 'url': str}]"""
        self._anchor(anchor)
        self._sections.append({'type': 'links', 'title': title, 'links': links})
        return self

    # ── レンダリング ────────────────────────────────────
    @staticmethod
    def _links_html(links: list) -> str:
        def safe_url(value) -> str:
            raw = str(value or '').strip()
            parsed = urlparse(raw)
            return raw if parsed.scheme == 'https' and parsed.netloc else ''

        return ''.join(
            '<div class="gh-linkrow">'
            + (f'<span class="gh-linkrow-cat">{_e(l.get("cat",""))}</span>' if l.get('cat') else '')
            + f'<a href="{_e(safe_url(l.get("url")))}" target="_blank" rel="noopener noreferrer">'
              f'{_e(l.get("label") or l.get("url",""))}</a></div>'
            for l in links)

    def _r_accordion(self, s: dict) -> str:
        chips = '<button type="button" class="gh-chip on" data-f="all">すべて</button>'
        for f in s['filters']:
            hl = ' hl' if f.get('hl') else ''
            chips += (f'<button type="button" class="gh-chip{hl}" '
                      f'data-f="{_e(f["key"])}">{_e(f["label"])}</button>')
        ph = _e(s['ph'] or 'キーワードで絞り込み')
        toolbar = (f'<div class="gh-toolbar">'
                   f'<input type="search" class="gh-search" placeholder="{ph}" aria-label="検索">'
                   f'{chips}<span class="gh-count"></span></div>')

        cards = ''
        for n, it in enumerate(s['items'], 1):
            iid = it.get('id') or f'gh-item-{n}'
            badges = ''.join(
                f'<span class="gh-badge {_e(b.get("color","navy"))}">{_e(b["text"])}</span>'
                for b in it.get('badges', []))
            cols = ''
            if it.get('columns'):
                cols = ('<div class="gh-subgrid">' + ''.join(
                    f'<div class="gh-block"><div class="gh-block-t">{_e(c.get("title",""))}</div>'
                    f'<div class="gh-block-b">{c.get("html") or _e(c.get("body",""))}</div></div>'
                    for c in it['columns']) + '</div>')
            blocks = ''.join(
                f'<div class="gh-block"><div class="gh-block-t">{_e(b.get("title",""))}</div>'
                f'<div class="gh-block-b{" impact" if b.get("impact") else ""}">'
                f'{b.get("html") or _e(b.get("body",""))}</div></div>'
                for b in it.get('blocks', []))
            tags = ''
            if it.get('tags'):
                tags = ('<div class="gh-block"><div class="gh-block-t">キーポイント</div>'
                        '<div class="gh-taglist">'
                        + ''.join(f'<span class="gh-tag">{_e(t)}</span>' for t in it['tags'])
                        + '</div></div>')
            links = ''
            if it.get('links'):
                links = ('<div class="gh-block"><div class="gh-block-t">引用・出典</div>'
                         + self._links_html(it['links']) + '</div>')
            blob = it.get('search') or ' '.join(filter(None, [
                it.get('name', ''), it.get('meta', ''),
                ' '.join(str(b.get('body', '')) for b in it.get('blocks', [])),
                ' '.join(str(c.get('body', '')) for c in it.get('columns', [])),
                ' '.join(it.get('tags', [])),
            ]))
            cards += (
                f'<article class="gh-item{" accent" if it.get("accent") else ""}" id="{_e(iid)}" '
                f'data-filters="{_e("|".join(it.get("filters", [])))}" data-search="{_e(blob)}">'
                f'<div class="gh-item-head" role="button" tabindex="0" aria-expanded="false">'
                f'<span class="gh-caret">▶</span>'
                f'<span class="gh-item-name">{_e(it.get("name",""))}</span>{badges}'
                f'<span class="gh-item-meta">{_e(it.get("meta",""))}</span>'
                f'<span class="gh-item-right">{_e(it.get("right",""))}</span></div>'
                f'<div class="gh-item-body"><div><div class="gh-item-inner">'
                f'{cols}{blocks}{tags}{links}'
                f'</div></div></div></article>')

        note = (f'<div class="gh-card" style="margin-block-start:12px"><div class="gh-card-body" '
                f'style="font-size:14px;color:var(--gh-text-muted)">{_e(s["note"])}</div></div>'
                if s.get('note') else '')
        return (f'<div class="gh-section">'
                f'<div class="gh-section-title">{_e(s["title"])}</div>'
                f'{toolbar}<div class="gh-acc">{cards}</div>'
                f'<div class="gh-empty">該当する項目がありません。検索条件を変更してください。</div>'
                f'{note}</div>')

    def _r_timeline(self, s: dict) -> str:
        rows = ''.join(
            f'<div class="gh-tl-row{" accent" if r.get("accent") else ""}"'
            + (f' data-jump="{_e(r["jump"])}"' if r.get('jump') else '')
            + f'><span class="gh-tl-date">{_e(r.get("date",""))}</span>'
              f'<span class="gh-tl-text">{_e(r.get("text",""))}</span></div>'
            for r in s['rows'])
        return (f'<div class="gh-section">'
                f'<div class="gh-section-title">{_e(s["title"])}</div>'
                f'<div class="gh-tl">{rows}</div></div>')

    def _r_tabs(self, s: dict) -> str:
        g = s['group']
        btns, panels = '', ''
        for i, t in enumerate(s['tabs']):
            pid = f'{g}-p{i}'
            on = ' on' if i == 0 else ''
            btns += (f'<button type="button" class="gh-tab{on}" data-tab="{pid}">'
                     f'{_e(t.get("label",""))}</button>')
            panels += f'<div class="gh-panel{on}" id="{pid}" data-group="{g}">{t.get("html","")}</div>'
        return (f'<div class="gh-section">'
                f'<div class="gh-section-title">{_e(s["title"])}</div>'
                f'<div class="gh-tabs" data-group="{g}">{btns}</div>{panels}</div>')

    def _r_checklist(self, s: dict) -> str:
        rows = ''.join(
            f'<label class="gh-check"><input type="checkbox" data-k="{i}">'
            f'<span class="gh-check-main">'
            f'<span class="gh-check-text">{_e(it.get("text",""))}</span>'
            + (f'<span class="gh-check-meta">{_e(it["meta"])}</span>' if it.get('meta') else '')
            + '</span></label>'
            for i, it in enumerate(s['items']))
        note = (f'<div class="gh-card" style="margin-block-start:10px"><div class="gh-card-body" '
                f'style="font-size:14px;color:var(--gh-text-muted)">{_e(s["note"])}</div></div>'
                if s.get('note') else '')
        return (f'<div class="gh-section">'
                f'<div class="gh-section-title">{_e(s["title"])}</div>'
                f'<div class="gh-checklist" data-key="{_e(s["key"])}">'
                f'<div class="gh-progress-wrap">'
                f'<div class="gh-progress-label">0 / {len(s["items"])} 件 完了</div>'
                f'<div class="gh-progress"><div class="gh-progress-fill"></div></div></div>'
                f'{rows}</div>{note}</div>')

    def _r_links(self, s: dict) -> str:
        return (f'<div class="gh-section">'
                f'<div class="gh-section-title">{_e(s["title"])}</div>'
                f'<div class="gh-card"><div>{self._links_html(s["links"])}</div></div></div>')

    def _r_section(self, s: dict) -> str:
        t = s.get('type', '')
        if t == 'accordion':  return self._r_accordion(s)
        if t == 'timeline':   return self._r_timeline(s)
        if t == 'tabs':       return self._r_tabs(s)
        if t == 'checklist':  return self._r_checklist(s)
        if t == 'links':      return self._r_links(s)
        return super()._r_section(s)

    def _r_nav(self) -> str:
        if not self._nav and not self._nav_buttons:
            return ''
        links = ''.join(f'<a href="#{_e(i)}">{_e(l)}</a>' for i, l in self._nav)
        btns = ''.join(f'<button type="button" class="gh-iconbtn" {b["attr"]}>{_e(b["label"])}</button>'
                       for b in self._nav_buttons)
        spacer = '<span class="gh-nav-spacer"></span>' if btns else ''
        return f'<nav class="gh-nav"><div class="gh-nav-inner">{links}{spacer}{btns}</div></nav>'

    # ── Build ───────────────────────────────────────────
    def build(self) -> str:
        base = super().build()
        int_css = _INT_CSS_FILE.read_text(encoding='utf-8') if _INT_CSS_FILE.exists() else ''
        # ダークモード対応のmeta。テーマは同梱CSSで制御する。
        base = base.replace('<meta name="color-scheme" content="light">',
                            '<meta name="color-scheme" content="light dark">')
        base = base.replace('</style>', int_css + '\n  </style>')
        nav = self._r_nav()
        if nav:
            base = base.replace('<body>', '<body>\n' + nav)
        totop = ('<button type="button" class="gh-totop" aria-label="トップへ戻る">↑</button>'
                 if self._show_totop else '')
        base = base.replace('</body>', f'{totop}\n<script>{_JS}</script>\n</body>')
        return base


__all__ = ['InteractiveReport']
