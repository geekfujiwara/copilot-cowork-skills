"""edit-plan.json からプレビュー MP4 を書き出す（ffmpeg + Pillow。ブラウザ不要）。
usage: python render_preview.py PLAN.json OUT.mp4 [--stills 5,20,40] [--font PATH] [--crf 20]
--stills を付けると指定時刻（出力タイムライン秒）の静止画だけ書き出して確認できる。"""
import argparse, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import *

ap = argparse.ArgumentParser(); ap.add_argument("plan"); ap.add_argument("out")
ap.add_argument("--stills", default=""); ap.add_argument("--font"); ap.add_argument("--crf", default="20")
A = ap.parse_args()
P = load_plan(A.plan); FONT = resolve_font(A.font); print("font:", FONT)
SW, SH = P["_src"]["width"], P["_src"]["height"]
OW, OH, FPS = P["output"]["width"], P["output"]["height"], P["output"]["fps"]
ST = P["style"]; ACC = hex2rgb(ST["accent"]); HL = hex2rgb(ST["highlight"]); BG = hex2rgb(ST["background"])
ZD, MARGIN = ST["zoom_seconds"], ST["zoom_margin"]
# fit source into output (letterbox)
K = min(OW/SW, OH/SH); FW, FH = int(round(SW*K/2)*2), int(round(SH*K/2)*2); OX, OY = (OW-FW)//2, (OH-FH)//2
U = OH/1080  # UI scale

def ease(x): x = max(0, min(1, x)); return 4*x**3 if x < .5 else 1-(-2*x+2)**3/2
_fc = {}
def F(sz, w="Bold"):
    k = (int(sz*U), w)
    if k not in _fc: _fc[k] = load_font(FONT, k[0], w)
    return _fc[k]

def zoom_at(kfs, t):
    rects = [(k[0], fit_rect(k[1], SW, SH, MARGIN)) for k in kfs]; cur = rects[0][1]
    for i in range(1, len(rects)):
        ts, r = rects[i]
        if t < ts: break
        p = ease((t-ts)/ZD); prev = rects[i-1][1]; cur = tuple(a+(b-a)*p for a, b in zip(prev, r))
    return cur

_cc = {}
def callout_img(c):
    k = (c.get("step", ""), c["title"], c.get("sub", ""))
    if k in _cc: return _cc[k]
    ft, fs, fc = F(46), F(28, "Regular"), F(24)
    pad = int(36*U); w = int(max(ft.getlength(c["title"]), fs.getlength(c.get("sub", ""))) + pad*2 + 24*U)
    h = int((190 if c.get("sub") else 140)*U); e = int(20*U)
    im = Image.new("RGBA", (w+2*e, h+2*e), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((e, e+4, w+e, h+e+4), int(22*U), fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.rounded_rectangle((e, e, w+e, h+e), int(22*U), fill=BG+(236,), outline=ACC+(120,), width=2)
    if ST.get("callout_accent_bar"): d.rounded_rectangle((e, e, e+int(10*U), h+e), 4, fill=ACC+(255,))
    x = e+pad; y = e+int(20*U)
    if c.get("step"):
        cw = fc.getlength(c["step"])+28*U; d.rounded_rectangle((x, y, x+cw, y+38*U), int(19*U), fill=ACC+(255,))
        d.text((x+14*U, y+3*U), c["step"], font=fc, fill=BG); y += int(50*U)
    d.text((x, y), c["title"], font=ft, fill=(255, 255, 255)); y += int(62*U)
    if c.get("sub"): d.text((x+2, y), c["sub"], font=fs, fill=(190, 205, 225))
    _cc[k] = im; return im

def card(p, t, dur):
    im = Image.new("RGB", (OW, OH), BG)
    g = Image.new("L", (OW, OH), 0); ImageDraw.Draw(g).ellipse((OW*.15, -OH*.4, OW*.85, OH*.7), fill=90)
    im.paste(Image.new("RGB", (OW, OH), tuple(min(255, int(c*0.5+40)) for c in ACC)), mask=g.filter(ImageFilter.GaussianBlur(160)))
    d = ImageDraw.Draw(im); a = ease(t/.8); fade = min(1, (dur-t)/.5); al = max(0, min(a, fade)); dy = int((1-a)*30)
    def txt(y, s, f, col):
        if not s: return
        c = tuple(int(BG[i]+(col[i]-BG[i])*al) for i in range(3)); d.text((OW/2-f.getlength(s)/2, y*U+dy), s, font=f, fill=c)
    txt(330, p.get("kicker", ""), F(34), ACC); txt(400, p.get("title", ""), F(104), (255, 255, 255))
    lw = int(560*U*ease((t-.3)/.8)*fade)
    if lw > 0: d.rounded_rectangle((OW/2-lw/2, 560*U+dy, OW/2+lw/2, 566*U+dy), 3, fill=ACC)
    txt(610, p.get("sub", ""), F(40, "Regular"), (200, 214, 235)); return im

def seg_frame(arr, s, t):
    r = zoom_at(s["zoom"], t)
    fr = Image.fromarray(arr).crop(tuple(int(round(v)) for v in r)).resize((FW, FH), Image.BICUBIC)
    canvas = Image.new("RGB", (OW, OH), BG); canvas.paste(fr, (OX, OY))
    sx, sy = FW/(r[2]-r[0]), FH/(r[3]-r[1]); ov = None
    for h in s["highlights"]:
        a0, a1 = h["t"]
        if not (a0 <= t <= a1): continue
        al = min(1, (t-a0)/.35, (a1-t)/.35); x0, y0, x1, y1 = h["rect"]
        b = ((x0-r[0])*sx+OX, (y0-r[1])*sy+OY, (x1-r[0])*sx+OX, (y1-r[1])*sy+OY)
        pad = 6+4*(.5+.5*math.sin((t-a0)*5)); bb = (b[0]-pad, b[1]-pad, b[2]+pad, b[3]+pad)
        dim = Image.new("RGBA", (OW, OH), (0, 0, 0, int(110*al))); ImageDraw.Draw(dim).rounded_rectangle(bb, 14, fill=(0, 0, 0, 0))
        ov = dim if ov is None else Image.alpha_composite(ov, dim)
        ImageDraw.Draw(ov).rounded_rectangle(bb, 14, outline=HL+(int(255*al),), width=5)
    for c in s["callouts"]:
        a0, a1 = c["t"]
        if not (a0 <= t <= a1): continue
        ov = ov or Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); ci = callout_img(c)
        al = max(0, min(1, (t-a0)/.4, (a1-t)/.4)); dy = int((1-ease(min(1, (t-a0)/.5)))*40)
        ci2 = ci.copy(); ci2.putalpha(ci.getchannel("A").point(lambda v: int(v*al)))
        pos = c.get("position", "bottom-left"); m = int(40*U)
        x = m if "left" in pos else OW-ci.width-m; y = OH-ci.height-m+dy if "bottom" in pos else m+dy
        ov.alpha_composite(ci2, (x, y))
    if ov is not None: canvas = Image.alpha_composite(canvas.convert("RGBA"), ov).convert("RGB")
    return canvas

def read_seg(s0, d):
    p = subprocess.Popen([ffmpeg(), "-v", "quiet", "-ss", str(s0), "-i", P["source"], "-t", str(d), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-r", str(FPS), "-"], stdout=subprocess.PIPE); n = SW*SH*3
    try:
        while True:
            b = p.stdout.read(n)
            if len(b) < n: break
            yield np.frombuffer(b, np.uint8).reshape(SH, SW, 3)
    finally: p.kill()

TL, TOTAL = timeline(P)
if A.stills:
    base = os.path.splitext(A.out)[0]
    for T in [float(x) for x in A.stills.split(",")]:
        for kind, st, d, p in TL:
            if st <= T < st+d:
                t = T-st
                im = seg_frame(next(read_seg(p["src"][0]+t, .2)), p, t) if kind == "seg" else card(p, t, d)
                im.save(f"{base}_still_{T:06.2f}.png"); print("still:", f"{base}_still_{T:06.2f}.png")
    sys.exit()

tmpv = A.out+".video.mp4"; tmpa = A.out+".audio.m4a"
enc = subprocess.Popen([ffmpeg(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", A.crf, "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
for kind, st, d, p in TL:
    nf = int(round(d*FPS))
    if kind == "seg":
        i, last = 0, None
        for arr in read_seg(p["src"][0], d):
            if i >= nf: break
            enc.stdin.write(seg_frame(arr, p, i/FPS).tobytes()); i += 1; last = arr
        while i < nf: enc.stdin.write(seg_frame(last, p, i/FPS).tobytes()); i += 1
    else:
        for i in range(nf): enc.stdin.write(card(p, i/FPS, d).tobytes())
    print(f"{kind} @ {st:.1f}s rendered", flush=True)
enc.stdin.close(); enc.wait()

# audio: silence for cards, source audio per segment with 30 ms fades (or full silence if source has none)
ins, lab, flt, idx = [], [], [], 0
def silence(d):
    global idx; ins.extend(["-f", "lavfi", "-t", f"{d}", "-i", "anullsrc=r=48000:cl=stereo"]); lab.append(f"[{idx}:a]"); idx += 1
for kind, st, d, p in TL:
    if kind != "seg" or not P["_src"]["has_audio"] or p.get("mute"): silence(d); continue
    ins.extend(["-ss", str(p["src"][0]), "-t", str(d), "-i", P["source"]])
    flt.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{d},afade=t=in:d=0.03,afade=t=out:st={d-0.03}:d=0.03[a{idx}]")
    lab.append(f"[a{idx}]"); idx += 1
fc = (";".join(flt)+";" if flt else "")+"".join(lab)+f"concat=n={len(lab)}:v=0:a=1[aout]"
subprocess.run([ffmpeg(), "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", "[aout]", "-c:a", "aac", "-b:a", "160k", tmpa], check=True)
subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", tmpv, "-i", tmpa, "-c", "copy", "-shortest", "-movflags", "+faststart", A.out], check=True)
os.remove(tmpv); os.remove(tmpa); print(f"OK {A.out} ({TOTAL:.1f}s)")
