#!/usr/bin/env python3
"""Self-contained interactive report generator.

Module usage:
    import sys
    sys.path.insert(0, str(Path('scripts').resolve()))
    from report import Report

    r = Report('レポートタイトル', subtitle='サブタイトル', date='<対象日>')
    r.set_header_stats([
        {'value': '99.5%', 'label': '稼働率'},
        {'value': '4.5',   'label': '顧客満足度'},
    ])
    r.add_kpi_grid([
        {'label': '稼働率', 'value': '99.5%', 'delta': '▲+0.3pt', 'trend': 'good'},
    ], title='主要 KPI')
    r.add_card_grid('改善提案', cards=[
        {'title': '提案1', 'body': '内容', 'icon': 'copilot', 'effect': '期待効果'},
    ], cols=3)
    r.add_table('実績比較', headers=['KPI','前年','今年','変化'], rows=[...])
    r.add_actions('次のアクション', items=[
        {'text': 'アクション内容', 'owner': '担当者', 'date': '期限'},
    ])
    r.save('output/report.html')

CLI usage:
    python report.py --config content.json --out output/report.html
"""

import json
import base64
import argparse
import html as _html_mod
from pathlib import Path
from datetime import datetime

_SKILL_DIR = Path(__file__).resolve().parent.parent
_CSS_FILE = _SKILL_DIR / 'scripts' / 'report.css'
_INT_CSS_FILE = _CSS_FILE.parent / 'interactive.css'
_ICONS_DIR = _SKILL_DIR / 'images'


# ── Utilities ────────────────────────────────────────────────

def _e(text) -> str:
    """HTML-escape a value."""
    return _html_mod.escape(str(text)) if text is not None else ''


def _icon_b64(name: str) -> str:
    """Return inline data URI for an icon PNG (empty string if not found)."""
    if not name:
        return ''
    fname = name if name.endswith('.png') else f'{name}.png'
    p = _ICONS_DIR / fname
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


def _img_b64(path: str) -> str:
    """Return inline data URI for any image file."""
    if not path:
        return ''
    p = Path(path)
    if not p.exists():
        return ''
    ext = p.suffix.lower().lstrip('.')
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
            'gif': 'image/gif', 'svg': 'image/svg+xml'}.get(ext, 'image/png')
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()


# ══════════════════════════════════════════════════════════════
# Report — main builder class
# ══════════════════════════════════════════════════════════════

class Report:
    """
    Builds self-contained HTML reports using bundled styles.
    All methods return self for chaining.
    """

    def __init__(self, title: str, subtitle: str = '',
                 label: str = '', date: str = ''):
        self.title    = title
        self.subtitle = subtitle
        self.label    = label
        self.date     = date or datetime.now().strftime('%Y年%m月%d日')
        self._stats: list = []
        self._sections: list = []

    # ── Header ──────────────────────────────────────────────

    def set_header_stats(self, stats: list):
        """
        Set stats strip below header title.
        stats: [{'value': str, 'label': str}, ...]
        """
        self._stats = stats
        return self

    # ── Content sections ─────────────────────────────────────

    def add_kpi_grid(self, items: list, title: str = ''):
        """
        Add KPI metric card grid.
        items:
          label   str   — metric name
          value   str   — main value displayed large
          unit    str   — optional unit appended small (e.g. '/ 5', '時間')
          delta   str   — change text (e.g. '▲+0.3pt', '▼50%')
          trend   str   — 'good' | 'warn' | 'bad'  (badge color)
          prev    str   — previous value footnote
          accent  str   — card left-border color: 'hl'|'green'|'amber'|'red' (default navy)
        """
        self._sections.append({'type': 'kpi', 'title': title, 'items': items})
        return self

    def add_card_grid(self, title: str, cards: list, cols: int = 3):
        """
        Add content card grid.
        cards:
          title   str  — card heading (bold, navy-dark)
          body    str  — description text
          icon    str  — optional bundled icon filename without .png
          effect  str  — optional highlighted effect box
        """
        self._sections.append({'type': 'cards', 'title': title,
                                'cards': cards, 'cols': cols})
        return self

    def add_table(self, title: str, headers, rows: list):
        """
        Add a data table.
        headers: list of str  OR  list of {'text': str, 'align': 'start'|'end'|'center'}
        rows:    list of list  — each cell is str  OR  {'text': str, 'class': str}
                 Useful CSS classes for cells: 'num' 'imp' 'hl' 'ok' 'warn'
        """
        self._sections.append({'type': 'table', 'title': title,
                                'headers': headers, 'rows': rows})
        return self

    def add_divider(self, title: str, subtitle: str = '',
                    bg_image: str = ''):
        """
        Add a dark section divider (navy gradient + optional background image).
        bg_image: absolute path to an image file (embedded as base64).
        """
        self._sections.append({'type': 'divider', 'title': title,
                                'subtitle': subtitle, 'bg_image': bg_image})
        return self

    def add_summary(self, title: str, body: str):
        """Add a highlighted summary / executive summary box."""
        self._sections.append({'type': 'summary', 'title': title, 'body': body})
        return self

    def add_actions(self, title: str, items: list):
        """
        Add numbered action item list.
        items:
          text   str  — action description
          owner  str  — responsible party
          date   str  — deadline or period
        """
        self._sections.append({'type': 'actions', 'title': title, 'items': items})
        return self

    def add_raw(self, html_fragment: str):
        """Insert raw HTML fragment (advanced use — ensure it's self-contained)."""
        self._sections.append({'type': 'raw', 'html': html_fragment})
        return self

    # ── Rendering ────────────────────────────────────────────

    def _r_header(self) -> str:
        label_h = f'<div class="gh-header-label">{_e(self.label)}</div>' if self.label else ''
        meta    = _e(self.subtitle) + ('　｜　' + _e(self.date) if self.subtitle else _e(self.date))
        stats_h = ''
        if self._stats:
            items = ''.join(
                f'<div class="gh-header-stat">'
                f'<div class="v">{_e(s.get("value",""))}</div>'
                f'<div class="l">{_e(s.get("label",""))}</div>'
                f'</div>'
                for s in self._stats
            )
            stats_h = f'<div class="gh-header-stats">{items}</div>'
        return (f'<header class="gh-header">\n'
                f'  {label_h}\n'
                f'  <h1 class="gh-header-title">{_e(self.title)}</h1>\n'
                f'  <p class="gh-header-meta">{meta}</p>\n'
                f'  {stats_h}\n'
                f'</header>')

    def _r_kpi(self, s: dict) -> str:
        cards = ''
        for item in s.get('items', []):
            accent = item.get('accent', '')
            cls    = f'gh-kpi-card {accent}'.strip()
            unit_h  = f' <span class="gh-kpi-unit">{_e(item["unit"])}</span>' if item.get('unit') else ''
            delta_h = ''
            if item.get('delta'):
                trend = _e(item.get('trend', ''))
                delta_h = f'<div class="gh-kpi-delta {trend}">{_e(item["delta"])}</div>'
            prev_h = f'<span class="gh-kpi-prev">{_e(item["prev"])}</span>' if item.get('prev') else ''
            cards += (f'<div class="{cls}">\n'
                      f'  <div class="gh-kpi-label">{_e(item.get("label",""))}</div>\n'
                      f'  <div class="gh-kpi-value">{_e(item.get("value",""))}{unit_h}</div>\n'
                      f'  {delta_h}{prev_h}\n'
                      f'</div>\n')
        ttl = f'<div class="gh-section-title">{_e(s["title"])}</div>\n' if s.get('title') else ''
        return f'<div class="gh-section">\n{ttl}<div class="gh-kpi-grid">\n{cards}</div>\n</div>\n'

    def _r_cards(self, s: dict) -> str:
        cols = s.get('cols', 3)
        cards = ''
        for c in s.get('cards', []):
            icon_b64 = _icon_b64(c.get('icon', ''))
            icon_h   = (f'<img class="gh-card-icon" src="{icon_b64}" alt="{_e(c.get("icon",""))}">\n'
                        if icon_b64 else '')
            effect_h = (f'<div class="gh-card-effect">{_e(c.get("effect",""))}</div>\n'
                        if c.get('effect') else '')
            cards += (f'<div class="gh-card">\n'
                      f'  {icon_h}'
                      f'  <div class="gh-card-title">{_e(c.get("title",""))}</div>\n'
                      f'  <div class="gh-card-body">{_e(c.get("body",""))}</div>\n'
                      f'  {effect_h}'
                      f'</div>\n')
        ttl = f'<div class="gh-section-title">{_e(s["title"])}</div>\n' if s.get('title') else ''
        return (f'<div class="gh-section">\n{ttl}'
                f'<div class="gh-card-grid cols-{cols}">\n{cards}</div>\n</div>\n')

    def _r_table(self, s: dict) -> str:
        hdrs = ''
        for h in s.get('headers', []):
            if isinstance(h, dict):
                align = h.get('align', 'start')
                hdrs += f'<th style="text-align:{align}">{_e(h.get("text",""))}</th>'
            else:
                hdrs += f'<th>{_e(str(h))}</th>'
        rows = ''
        for row in s.get('rows', []):
            cells = ''
            for cell in row:
                if isinstance(cell, dict):
                    cells += f'<td class="{_e(cell.get("class",""))}">{_e(cell.get("text",""))}</td>'
                else:
                    cells += f'<td>{_e(str(cell))}</td>'
            rows += f'<tr>{cells}</tr>\n'
        ttl = f'<div class="gh-section-title">{_e(s["title"])}</div>\n' if s.get('title') else ''
        return (f'<div class="gh-section">\n{ttl}'
                f'<div class="gh-table-wrap">\n'
                f'  <table class="gh-table">\n'
                f'    <thead><tr>{hdrs}</tr></thead>\n'
                f'    <tbody>\n{rows}    </tbody>\n'
                f'  </table>\n</div>\n</div>\n')

    def _r_divider(self, s: dict) -> str:
        style = ''
        bg_b64 = _img_b64(s.get('bg_image', ''))
        if bg_b64:
            style = f' style="--gh-div-bg-img:url(\'{bg_b64}\')"'
        sub_h = (f'<p class="gh-divider-sub">{_e(s.get("subtitle",""))}</p>'
                 if s.get('subtitle') else '')
        return (f'<div class="gh-divider"{style}>\n'
                f'  <div class="gh-divider-title">{_e(s.get("title",""))}</div>\n'
                f'  {sub_h}\n</div>\n')

    def _r_summary(self, s: dict) -> str:
        return (f'<div class="gh-section">\n'
                f'<div class="gh-summary">\n'
                f'  <div class="gh-summary-title">{_e(s.get("title",""))}</div>\n'
                f'  <p>{_e(s.get("body",""))}</p>\n'
                f'</div>\n</div>\n')

    def _r_actions(self, s: dict) -> str:
        items = ''
        for i, item in enumerate(s.get('items', []), 1):
            owner_h = (f'<span class="gh-action-owner">{_e(item.get("owner",""))}</span>'
                       if item.get('owner') else '<span></span>')
            date_h  = (f'<span class="gh-action-date">{_e(item.get("date",""))}</span>'
                       if item.get('date') else '<span></span>')
            items += (f'<div class="gh-action-item">\n'
                      f'  <div class="gh-action-num">{i}</div>\n'
                      f'  <div class="gh-action-text">{_e(item.get("text",""))}</div>\n'
                      f'  {owner_h}\n  {date_h}\n'
                      f'</div>\n')
        ttl = f'<div class="gh-section-title">{_e(s["title"])}</div>\n' if s.get('title') else ''
        return (f'<div class="gh-section">\n{ttl}'
                f'<div class="gh-action-list">\n{items}</div>\n</div>\n')

    def _r_section(self, s: dict) -> str:
        t = s.get('type', '')
        if t == 'kpi':      return self._r_kpi(s)
        if t == 'cards':    return self._r_cards(s)
        if t == 'table':    return self._r_table(s)
        if t == 'divider':  return self._r_divider(s)
        if t == 'summary':  return self._r_summary(s)
        if t == 'actions':  return self._r_actions(s)
        if t == 'raw':      return s.get('html', '')
        return ''

    # ── Build & Save ─────────────────────────────────────────

    def build(self) -> str:
        css  = _CSS_FILE.read_text(encoding='utf-8') if _CSS_FILE.exists() else ''
        body = '\n'.join(self._r_section(s) for s in self._sections)
        footer = (f'<footer class="gh-footer">'
                  f'<span>{_e(self.title)}</span>'
                  f'<span>{_e(self.date)}</span>'
                  f'</footer>')
        return f"""<!DOCTYPE html>
<html lang="ja" dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <title>{_e(self.title)}</title>
  <style>
{css}
  </style>
</head>
<body>
{self._r_header()}
<main class="gh-main">
{body}
</main>
{footer}
</body>
</html>"""

    def save(self, output_path: str) -> Path:
        """Write the HTML to output_path. Creates parent dirs automatically."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.build(), encoding='utf-8')
        return p


# ── CLI ──────────────────────────────────────────────────────

def _from_config(cfg: dict) -> Report:
    r = Report(
        title    = cfg.get('title', ''),
        subtitle = cfg.get('subtitle', ''),
        label    = cfg.get('label', ''),
        date     = cfg.get('date', ''),
    )
    if cfg.get('stats'):
        r.set_header_stats(cfg['stats'])
    dispatch = {
        'kpi':     lambda s: r.add_kpi_grid(s.get('items', []), s.get('title', '')),
        'cards':   lambda s: r.add_card_grid(s.get('title',''), s.get('cards',[]), s.get('cols',3)),
        'table':   lambda s: r.add_table(s.get('title',''), s.get('headers',[]), s.get('rows',[])),
        'divider': lambda s: r.add_divider(s.get('title',''), s.get('subtitle',''), s.get('bg_image','')),
        'summary': lambda s: r.add_summary(s.get('title',''), s.get('body','')),
        'actions': lambda s: r.add_actions(s.get('title',''), s.get('items',[])),
        'raw':     lambda s: r.add_raw(s.get('html','')),
    }
    for s in cfg.get('sections', []):
        fn = dispatch.get(s.get('type',''))
        if fn:
            fn(s)
    return r


def main():
    parser = argparse.ArgumentParser(description='interactive-report generator')
    parser.add_argument('--config', required=True,
                        help='Path to JSON config file')
    parser.add_argument('--out',    required=True,
                        help='Output HTML file path (e.g. output/report.html)')
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    out = _from_config(cfg).save(args.out)
    print(f'Generated: {out}  ({out.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
