#!/usr/bin/env python3
"""構造化されたアカウント計画から自己完結型HTMLレポートを生成する。"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

THEME = """
:root{color-scheme:light;--cp-bg:#f7f4ef;--cp-bg-elevated:#fcfbf8;--cp-surface:#fff;--cp-surface-soft:#f5f5f5;--cp-border:#dedede;--cp-border-strong:#919191;--cp-text:#242424;--cp-text-muted:#5c5c5c;--cp-text-soft:#6f6f6f;--cp-accent:#b11f4b;--cp-accent-hover:#9a1a41;--cp-accent-soft:rgba(177,31,75,.08);--cp-accent-fg:#fff;--cp-success:#16a34a;--cp-danger:#dc2626;--cp-warning:#f59e0b;--cp-link:#0078d4;--cp-shadow:0 18px 48px rgba(0,0,0,.12);--cp-overlay:rgba(255,255,255,.8);--cp-panel:rgba(255,255,255,.86);--cp-panel-strong:rgba(255,255,255,.96);--cp-sheen:rgba(255,255,255,.55);--cp-highlight:rgba(177,31,75,.12)}
html[data-theme=dark]{color-scheme:dark;--cp-bg:#3d3b3a;--cp-bg-elevated:#343231;--cp-surface:#292929;--cp-surface-soft:#2e2e2e;--cp-border:#474747;--cp-border-strong:#5f5f5f;--cp-text:#dedede;--cp-text-muted:#919191;--cp-text-soft:#b0b0b0;--cp-accent:#fd8ea1;--cp-accent-hover:#fb7b91;--cp-accent-soft:rgba(253,142,161,.14);--cp-accent-fg:#1a1a1a;--cp-success:#4ade80;--cp-danger:#f87171;--cp-warning:#fbbf24;--cp-link:#4da6ff;--cp-shadow:0 18px 48px rgba(0,0,0,.32);--cp-overlay:rgba(41,41,41,.88);--cp-panel:rgba(41,41,41,.72);--cp-panel-strong:rgba(41,41,41,.96);--cp-sheen:rgba(255,255,255,.04);--cp-highlight:rgba(253,142,161,.12)}
"""


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def money(value: object, currency: str) -> str:
    try:
        return f"{currency} {float(value):,.0f}"
    except (TypeError, ValueError):
        return f"{currency} —"


def table_rows(items: list[dict], fields: list[str]) -> str:
    return "".join(
        "<tr data-search='{}'>{}</tr>".format(
            esc(" ".join(str(item.get(field, "")) for field in fields).lower()),
            "".join(f"<td>{esc(item.get(field, '—'))}</td>" for field in fields),
        )
        for item in items
    ) or f"<tr><td colspan='{len(fields)}'>該当項目はありません</td></tr>"


def render(data: dict) -> str:
    currency = str(data.get("currency", ""))
    allocations = data.get("allocations", [])
    if not isinstance(allocations, list):
        raise ValueError("allocations must be an array")
    total = float(data.get("total_budget", 0))
    allocated = sum(float(item.get("amount", 0)) for item in allocations)
    remaining = total - allocated
    payload = (
        json.dumps(data, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )
    return f"""<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<script>(()=>{{const p=new URLSearchParams(location.search).get('scoutTheme');const t=p||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.setAttribute('data-theme',t)}})();</script>
<title>{esc(data.get('title', 'Account Plan'))}</title><style>{THEME}
*{{box-sizing:border-box}}body{{margin:0;background:var(--cp-bg);color:var(--cp-text);font-family:"Segoe UI",Aptos,Calibri,-apple-system,BlinkMacSystemFont,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px 20px}}header{{margin-block-end:24px}}h1{{margin:0;color:var(--cp-accent)}}.muted{{color:var(--cp-text-muted)}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.card,section{{background:var(--cp-surface);border:1px solid var(--cp-border);border-radius:16px;padding:16px;margin-block:16px;box-shadow:0 0 2px var(--cp-border)}}.value{{font-size:1.5rem;font-weight:700}}input,select{{padding:10px;border:1px solid var(--cp-border-strong);border-radius:.625rem;background:var(--cp-bg-elevated);color:var(--cp-text);margin-inline-end:8px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:start;border-block-end:1px solid var(--cp-border)}}th{{background:var(--cp-surface-soft)}}a{{color:var(--cp-link)}}.warn{{color:var(--cp-danger)}}@media(max-width:900px){{.cards{{grid-template-columns:1fr 1fr}}.scroll{{overflow:auto}}}}@media print{{.controls{{display:none}}.card,section{{box-shadow:none;break-inside:avoid}}}} </style></head>
<body><main><header><h1>{esc(data.get('title', 'Account Plan'))}</h1><p class='muted'>対象期間: {esc(data.get('period', '未確認'))}</p></header>
<div class='cards'><div class='card'><span class='muted'>総予算</span><div class='value'>{money(total,currency)}</div></div><div class='card'><span class='muted'>配分済み</span><div class='value'>{money(allocated,currency)}</div></div><div class='card'><span class='muted'>未配分</span><div class='value {'warn' if remaining < 0 else ''}'>{money(remaining,currency)}</div></div><div class='card'><span class='muted'>KPI</span><div class='value'>{len(data.get('kpis',[]))}</div></div></div>
<section class='controls'><label>検索 <input id='q' type='search' placeholder='アカウント・製品・状態'></label></section>
<section><h2>ゴール</h2><div class='scroll'><table><thead><tr><th>ゴール</th><th>アカウント</th><th>製品・サービス</th><th>状態</th></tr></thead><tbody>{table_rows(data.get('goals',[]),['name','account','offering','status'])}</tbody></table></div></section>
<section><h2>KPI</h2><div class='scroll'><table><thead><tr><th>KPI</th><th>基準値</th><th>目標</th><th>期限</th><th>根拠</th><th>確度</th></tr></thead><tbody>{table_rows(data.get('kpis',[]),['name','baseline','target','due','source','confidence'])}</tbody></table></div></section>
<section><h2>予算配分</h2><div class='scroll'><table><thead><tr><th>アカウント</th><th>製品・サービス</th><th>金額</th><th>状態</th><th>根拠</th></tr></thead><tbody>{table_rows(allocations,['account','offering','amount','status','rationale'])}</tbody></table></div></section>
<section><h2>実行ロードマップ</h2><div class='scroll'><table><thead><tr><th>ステップ</th><th>アカウント</th><th>製品・サービス</th><th>担当役割</th><th>期限</th><th>予算</th><th>状態</th></tr></thead><tbody>{table_rows(data.get('steps',[]),['name','account','offering','owner_role','due','budget','status'])}</tbody></table></div></section>
<section><h2>リスク・要確認</h2><div class='scroll'><table><thead><tr><th>項目</th><th>影響</th><th>対応</th></tr></thead><tbody>{table_rows(data.get('risks',[]),['name','impact','mitigation'])}</tbody></table></div></section>
<section><h2>根拠</h2><div class='scroll'><table><thead><tr><th>種別</th><th>タイトル</th><th>更新日</th><th>URL</th></tr></thead><tbody>{table_rows(data.get('sources',[]),['type','title','updated','url'])}</tbody></table></div></section>
<script type='application/json' id='plan-data'>{payload}</script><script>const q=document.getElementById('q');q.addEventListener('input',()=>{{const v=q.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.dataset.search.includes(v))}});</script></main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
