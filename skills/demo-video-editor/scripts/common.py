"""Shared helpers: ffmpeg discovery, plan loading, font resolution (Noto Sans JP default)."""
import json, os, shutil, subprocess, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FONT_DIR = os.path.join(SKILL, "assets", "fonts")
NOTO_URLS = [  # SIL Open Font License 1.1
    "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf",
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf",
]
SYSTEM_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/Library/Fonts/NotoSansJP-Bold.otf", os.path.expanduser("~/Library/Fonts/NotoSansJP-Bold.otf"),
    "C:/Windows/Fonts/NotoSansJP-VF.ttf", "C:/Windows/Fonts/NotoSansJP-Bold.ttf",
    os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP-VF.ttf"),
]
FALLBACK_FONTS = ["/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", "C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/meiryob.ttc"]

def ffmpeg():
    p = shutil.which("ffmpeg")
    if p: return p
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception: sys.exit("ffmpeg が見つかりません。ffmpeg をインストールしてください。")

def probe(path):
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    import re
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    vs = re.search(r"Video: .*?, (\d{2,5})x(\d{2,5})", out)
    fps = re.search(r"([\d.]+) fps", out)
    return dict(duration=int(dur[1])*3600+int(dur[2])*60+float(dur[3]) if dur else None,
                width=int(vs[1]) if vs else None, height=int(vs[2]) if vs else None,
                fps=float(fps[1]) if fps else None, has_audio="Audio:" in out)

def _has_japanese(path):
    try:
        from PIL import ImageFont
        f = ImageFont.truetype(path, 40)
        return f.getbbox("株")[2] - f.getbbox("株")[0] > 10 and f.getmask("株").getbbox() is not None
    except Exception: return False

def resolve_font(explicit=None, allow_download=True):
    """Noto Sans JP を最優先。順序: 明示指定/環境変数 → 同梱 assets/fonts → システム → ダウンロード。"""
    cands = [explicit, os.environ.get("DEMO_VIDEO_FONT")]
    if os.path.isdir(FONT_DIR):
        cands += sorted(os.path.join(FONT_DIR, f) for f in os.listdir(FONT_DIR)
                        if f.lower().endswith((".ttf", ".otf", ".ttc")) and "noto" in f.lower())
        cands += sorted(os.path.join(FONT_DIR, f) for f in os.listdir(FONT_DIR) if f.lower().endswith((".ttf", ".otf", ".ttc")))
    cands += SYSTEM_CANDIDATES
    for c in cands:
        if c and os.path.exists(c) and _has_japanese(c): return c
    if allow_download:
        os.makedirs(FONT_DIR, exist_ok=True)
        for u in NOTO_URLS:
            dst = os.path.join(FONT_DIR, "NotoSansJP" + os.path.splitext(u.split("/")[-1].replace("%5Bwght%5D", "-VF"))[1])
            try:
                urllib.request.urlretrieve(u, dst)
                if _has_japanese(dst): return dst
            except Exception: pass
    for c in FALLBACK_FONTS:
        if os.path.exists(c) and _has_japanese(c):
            print("警告: Noto Sans JP が無いため代替フォントを使用:", c); return c
    sys.exit("日本語フォント (Noto Sans JP) が見つかりません。NotoSansJP の .ttf/.otf を "
             f"{FONT_DIR} に置くか、--font で指定してください。")

def load_font(path, size, weight="Bold"):
    from PIL import ImageFont
    f = ImageFont.truetype(path, size)
    try: f.set_variation_by_name(weight)       # variable font (NotoSansJP[wght])
    except Exception: pass
    return f

def load_plan(path):
    with open(path, encoding="utf-8") as fh: plan = json.load(fh)
    base = os.path.dirname(os.path.abspath(path))
    if not os.path.isabs(plan["source"]): plan["source"] = os.path.join(base, plan["source"])
    if not os.path.exists(plan["source"]):
        sys.exit(f"元動画が見つかりません: {plan['source']}（edit-plan.json の source を確認してください）")
    info = probe(plan["source"])
    if not info.get("width"): sys.exit(f"動画として読み込めません: {plan['source']}")
    plan.setdefault("output", {}); o = plan["output"]
    o.setdefault("width", 1920); o.setdefault("height", 1080); o.setdefault("fps", 30)
    plan["_src"] = info
    st = plan.setdefault("style", {})
    st.setdefault("accent", "#4cc2ff"); st.setdefault("highlight", "#ffc83d"); st.setdefault("background", "#080d1a")
    st.setdefault("font_family", "Noto Sans JP"); st.setdefault("callout_accent_bar", False); st.setdefault("zoom_seconds", 0.9); st.setdefault("zoom_margin", 24)
    for s in plan["segments"]:
        s.setdefault("zoom", [[0, "full"]]); s.setdefault("callouts", []); s.setdefault("highlights", [])
    return plan

def timeline(plan):
    out, t = [], 0.0
    if plan.get("title"): out.append(("title", t, plan["title"].get("duration", 3.5), plan["title"])); t += out[-1][2]
    for s in plan["segments"]:
        d = s["src"][1] - s["src"][0]; out.append(("seg", t, d, s)); t += d
    if plan.get("end"): out.append(("end", t, plan["end"].get("duration", 3.5), plan["end"])); t += out[-1][2]
    return out, t

def hex2rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def fit_rect(r, sw, sh, margin):
    """Expand a source-pixel region to the source aspect ratio (plus margin) and clamp."""
    if r in ("full", None): return (0, 0, sw, sh)
    x0, y0, x1, y1 = r; x0 -= margin; y0 -= margin; x1 += margin; y1 += margin
    w, h = x1-x0, y1-y0; asp = sw/sh
    if w/h < asp: w2 = h*asp; cx = (x0+x1)/2; x0, x1 = cx-w2/2, cx+w2/2
    else: h2 = w/asp; cy = (y0+y1)/2; y0, y1 = cy-h2/2, cy+h2/2
    w, h = x1-x0, y1-y0
    if w >= sw or h >= sh: return (0, 0, sw, sh)
    x0 = min(max(x0, 0), sw-w); y0 = min(max(y0, 0), sh-h)
    return (x0, y0, x0+w, y0+h)
