# -*- coding: utf-8 -*-
"""
audit_skill.py — スキルの公開前品質ゲート。1 コマンドで 5 観点を機械チェックする。

skill-builder の「チェック・更新」フェーズで使う。汎用スクリプトで、対象スキルに依存しない。

チェック観点:
  1. 秘匿性 (secrets)   — メールアドレス / GUID / 外部ホスト / IP / トークンらしき文字列 /
                          テナント固有語 (--tenant-terms で追加) の混入
  2. 参照整合 (refs)     — SKILL.md から各コンポーネントへ直接/間接に到達できるか、
                          未参照の孤児が無いか、Markdown の相対リンクが切れていないか
  3. 簡潔性 (size)       — SKILL.md の文字数 (既定 5000 以下) と description 長 (既定 300 / 上限 1024)
  4. 階層 (layout)       — SKILL.md / references / scripts / images(assets) の分離、
                          想定外のトップレベル要素や __pycache__ 等の混入
    5. ライセンス (assets) — 再配布できない可能性の高いフォント等のバイナリ同梱
    6. 安全性 (safety)     — 外部データを命令として扱わないこと、送信時の明示確認、
                                                    ガードや承認を迂回する指示がないこと

使い方:
    python audit_skill.py "${COWORK_SKILLS_ROOT}/<name>"
    python audit_skill.py <dir> --json
    python audit_skill.py <dir> --tenant-terms "社名,内部コード,環境名"
    python audit_skill.py <dir> --max-skill-chars 5000 --max-desc-chars 300

終了コード: 0 = FAIL 無し / 1 = FAIL あり (WARN のみなら 0)
"""
import argparse
import json
import os
import re
import sys

# 再配布が問題になりやすい拡張子 (フォントは特に注意)
RISKY_BINARY_EXT = {".ttc", ".ttf", ".otf", ".woff", ".woff2", ".eot"}
# 除外してよい既知の技術ドメイン (XML 名前空間など)
ALLOWED_HOST_RE = re.compile(
    r"(schemas\.|w3\.org|openxmlformats|purl\.org|example\.(com|org)|"
    r"teams\.microsoft\.com|graph\.microsoft\.com|www\.google\.com|transit\.yahoo\.co\.jp)",
    re.I,
)
# スキルの標準レイアウト
STD_DIRS = {"references", "scripts", "images", "assets"}
STD_FILES_RE = re.compile(r"^(SKILL\.md|README\.md|LICENSE|NOTICE|config\.sample\.json|.*\.sample\..*)$")

TEXT_EXT = {".md", ".py", ".json", ".txt", ".yaml", ".yml", ".js", ".sh"}

PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "FAIL"),
    ("guid", re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "FAIL"),
    ("ipv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "WARN"),
    # 実際に値が代入されている形だけを拾う (語そのものの言及は除外)
    ("bearer_or_key", re.compile(
        r"(?i)((api[_-]?key|secret|password|token)\s*[:=]\s*[\"']?[A-Za-z0-9._\-]{8,}"
        r"|bearer\s+[A-Za-z0-9._-]{12,}|\bey[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,})"), "FAIL"),
    ("url_host", re.compile(r"https?://[A-Za-z0-9.-]+"), "WARN"),
]

# 誤検出を避ける文脈 (OData の @odata.bind、プレースホルダなど)
FALSE_POSITIVE_RE = re.compile(r"@odata|<[^>]*>|\{[^}]*\}|\bexample\b", re.I)
EXTERNAL_DATA_RE = re.compile(
    r"web_search|search_images|SearchM365|QueryGraph|ReadFileContent|GetMessage|transcript",
    re.I,
)
UNTRUSTED_DATA_GUARD_RE = re.compile(
    r"命令文.{0,30}データ|指示として.{0,12}(?:実行|従わ)|untrusted|prompt injection",
    re.I | re.S,
)
EXTERNAL_ACTION_RE = re.compile(
    r"SendEmail|SendDraftMessage|PostMessage|SendMessage", re.I
)
CONFIRMATION_RE = re.compile(
    r"明示.{0,24}(?:依頼|指示|確認|承認)|(?:確認|承認).{0,24}(?:送信|投稿|共有|公開)|confirm",
    re.I | re.S,
)
BYPASS_RE = re.compile(
    r"ガード.{0,16}(?:回避|迂回)(?!しな)|承認.{0,16}(?:不要|省略)(?!しな)|プレビュー.{0,16}なし",
    re.I | re.S,
)


def _result(check, status, detail=""):
    return {"check": check, "status": status, "detail": detail}


def iter_files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("__pycache__", ".git")]
        for f in fn:
            full = os.path.join(dp, f)
            yield os.path.relpath(full, root).replace("\\", "/"), full


def read_texts(root):
    texts = {}
    for rel, full in iter_files(root):
        if os.path.splitext(rel)[1].lower() in TEXT_EXT:
            try:
                texts[rel] = open(full, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                pass
    return texts


# --------------------------------------------------------------------------
# 1. 秘匿性
# --------------------------------------------------------------------------
def check_secrets(texts, tenant_terms):
    results = []
    hits = {}
    for rel, body in texts.items():
        if os.path.basename(rel) == os.path.basename(__file__):
            continue          # 検出器自身のパターン定義は対象外
        for line_no, line in enumerate(body.splitlines(), 1):
            if "audit_skill.py" in line or "PATTERNS" in line:
                continue      # 本スクリプトを説明している行は対象外
            for name, rx, sev in PATTERNS:
                for m in rx.finditer(line):
                    frag = m.group(0)
                    if name == "url_host" and ALLOWED_HOST_RE.search(frag):
                        continue
                    if name in ("email", "guid") and FALSE_POSITIVE_RE.search(line):
                        # プレースホルダや odata 記法の行は誤検出とみなす
                        if not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|jp|net|org)", frag):
                            continue
                    hits.setdefault((name, sev), []).append("%s:%d %s" % (rel, line_no, frag[:60]))

    for term in [t.strip() for t in tenant_terms if t.strip()]:
        for rel, body in texts.items():
            for line_no, line in enumerate(body.splitlines(), 1):
                if term in line:
                    hits.setdefault(("tenant_term:" + term, "FAIL"), []).append("%s:%d" % (rel, line_no))

    if not hits:
        results.append(_result("secrets", "PASS", "機微情報の検出なし"))
    else:
        for (name, sev), items in sorted(hits.items()):
            results.append(_result("secrets/" + name, sev,
                                   "%d 件: %s" % (len(items), "; ".join(items[:4]))))
    return results


# --------------------------------------------------------------------------
# 2. 参照整合
# --------------------------------------------------------------------------
def check_refs(root, texts):
    results = []
    files = sorted(rel for rel, _ in iter_files(root))
    if "SKILL.md" not in files:
        return [_result("refs", "FAIL", "SKILL.md がありません")]

    def refs_of(rel):
        body = texts.get(rel, "")
        out = set()
        for other in files:
            if other == rel:
                continue
            if other in body or os.path.basename(other) in body:
                out.add(other)
        return out

    seen, stack, direct = {"SKILL.md"}, ["SKILL.md"], refs_of("SKILL.md")
    while stack:
        for nxt in refs_of(stack.pop()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)

    orphans = [f for f in files if f not in seen]
    results.append(_result("refs/reachable", "FAIL" if orphans else "PASS",
                           "未参照: %s" % orphans if orphans
                           else "全 %d コンポーネントが SKILL.md から到達可能" % len(files)))

    broken = []
    for rel, body in texts.items():
        if not rel.endswith(".md"):
            continue
        for link in re.findall(r"\]\(([^)#][^)]*)\)", body):
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            if link in ("...", "…") or "<" in link or "{" in link:
                continue          # Markdown 記法例・実行時プレースホルダーはリンクではない
            tgt = os.path.normpath(os.path.join(os.path.dirname(rel), link.split("#")[0]))
            if not os.path.exists(os.path.join(root, tgt)):
                broken.append("%s -> %s" % (rel, link))
    results.append(_result("refs/links", "FAIL" if broken else "PASS",
                           "リンク切れ: %s" % broken[:5] if broken else "リンク切れなし"))
    return results


# --------------------------------------------------------------------------
# 3. 簡潔性
# --------------------------------------------------------------------------
def check_size(root, texts, max_skill, max_desc, hard_desc=1024):
    results = []
    body = texts.get("SKILL.md", "")
    n = len(body)
    results.append(_result("size/skill_md", "FAIL" if n > max_skill else "PASS",
                           "%d 文字 (上限 %d)" % (n, max_skill)))

    m = re.search(r"^---\s*\n(.*?)\n---\s*$", body, re.S | re.M)
    if not m:
        results.append(_result("size/description", "FAIL", "YAML front matter がありません"))
        return results
    fm = m.group(1)
    dm = re.search(r"^description:\s*(\|>?|>-?|\|-)?\s*\n((?:[ \t]+.*\n?)+)", fm, re.M)
    if dm:
        desc = re.sub(r"^[ \t]+", "", dm.group(2), flags=re.M).strip()
    else:
        dm = re.search(r"^description:\s*(.+)$", fm, re.M)
        desc = dm.group(1).strip() if dm else ""
    d = len(desc)
    status = "FAIL" if d > hard_desc else ("WARN" if d > max_desc else "PASS")
    results.append(_result("size/description", status,
                           "%d 文字 (推奨 %d / ハード上限 %d)" % (d, max_desc, hard_desc)))
    return results


# --------------------------------------------------------------------------
# 4. 階層
# --------------------------------------------------------------------------
def check_layout(root):
    results = []
    entries = sorted(os.listdir(root))
    stray = [e for e in entries
             if not (e in STD_DIRS or STD_FILES_RE.match(e))
             and not e.startswith(".")]
    results.append(_result("layout/toplevel", "WARN" if stray else "PASS",
                           "想定外のトップレベル: %s" % stray if stray
                           else "SKILL.md + %s の構成" % "/".join(d for d in STD_DIRS if os.path.isdir(os.path.join(root, d)))))

    junk = [rel for rel, _ in iter_files(root)
            if rel.endswith((".pyc", ".pyo", ".DS_Store")) or "__pycache__" in rel]
    # iter_files は __pycache__ を除外するので、実ディスク上を直接見る
    for dp, dn, fn in os.walk(root):
        if "__pycache__" in dp:
            junk.append(os.path.relpath(dp, root))
            break
    junk = sorted(set(junk))
    results.append(_result("layout/junk", "WARN" if junk else "PASS",
                           "ビルド副産物: %s" % junk[:5] if junk else "副産物なし"))

    misplaced = []
    for rel, _ in iter_files(root):
        ext = os.path.splitext(rel)[1].lower()
        top = rel.split("/")[0] if "/" in rel else ""
        if ext == ".py" and top != "scripts":
            misplaced.append(rel)
        if ext == ".md" and rel != "SKILL.md" and top != "references":
            misplaced.append(rel)
        if ext in (".png", ".jpg", ".jpeg", ".svg", ".webp") and top not in ("images", "assets"):
            misplaced.append(rel)
    results.append(_result("layout/placement", "WARN" if misplaced else "PASS",
                           "配置見直し: %s" % sorted(set(misplaced))[:5] if misplaced
                           else "各コンポーネントが正しい階層にある"))
    return results


# --------------------------------------------------------------------------
# 5. ライセンス
# --------------------------------------------------------------------------
def check_assets(root):
    risky = []
    for rel, full in iter_files(root):
        if os.path.splitext(rel)[1].lower() in RISKY_BINARY_EXT:
            risky.append("%s (%.1f MB)" % (rel, os.path.getsize(full) / 1048576.0))
    if risky:
        return [_result("assets/redistribution", "FAIL",
                        "再配布不可の可能性が高い同梱物: %s" % risky)]
    return [_result("assets/redistribution", "PASS", "ライセンス上問題になりやすい同梱物なし")]


# --------------------------------------------------------------------------
# 6. 外部データ・外部作用の安全性
# --------------------------------------------------------------------------
def check_safety(texts):
    body = texts.get("SKILL.md", "")
    results = []
    if EXTERNAL_DATA_RE.search(body) and not UNTRUSTED_DATA_GUARD_RE.search(body):
        results.append(_result(
            "safety/untrusted_data", "FAIL",
            "外部データ内の命令を指示として実行しないガードがありません",
        ))
    else:
        results.append(_result("safety/untrusted_data", "PASS", "外部データの扱いを確認"))

    if EXTERNAL_ACTION_RE.search(body) and not CONFIRMATION_RE.search(body):
        results.append(_result(
            "safety/external_action", "FAIL",
            "送信・投稿・共有・公開に明示的な確認ガードがありません",
        ))
    else:
        results.append(_result("safety/external_action", "PASS", "外部作用の確認ガードを確認"))

    if BYPASS_RE.search(body):
        results.append(_result("safety/bypass", "FAIL", "ガードまたは承認を迂回する指示があります"))
    else:
        results.append(_result("safety/bypass", "PASS", "ガード回避の指示なし"))
    return results


# --------------------------------------------------------------------------
def audit(root, tenant_terms=(), max_skill=5000, max_desc=300):
    texts = read_texts(root)
    results = []
    results += check_secrets(texts, tenant_terms)
    results += check_refs(root, texts)
    results += check_size(root, texts, max_skill, max_desc)
    results += check_layout(root)
    results += check_assets(root)
    results += check_safety(texts)
    return results


def main():
    ap = argparse.ArgumentParser(description="スキルの公開前品質ゲート")
    ap.add_argument("skill_dir")
    ap.add_argument("--tenant-terms", default="",
                    help="カンマ区切り。社名・内部コード・環境名など検出したい固有語")
    ap.add_argument("--max-skill-chars", type=int, default=5000)
    ap.add_argument("--max-desc-chars", type=int, default=300)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.skill_dir)
    if not os.path.isdir(root):
        print("ディレクトリがありません: %s" % root)
        sys.exit(1)

    results = audit(root, args.tenant_terms.split(","),
                    args.max_skill_chars, args.max_desc_chars)
    failed = [r for r in results if r["status"] == "FAIL"]
    warned = [r for r in results if r["status"] == "WARN"]

    if args.json:
        print(json.dumps({"skill": os.path.basename(root), "results": results,
                          "passed": not failed}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            mark = {"PASS": "OK  ", "WARN": "WARN", "FAIL": "FAIL"}[r["status"]]
            print("[%s] %-28s %s" % (mark, r["check"], r["detail"]))
        print("\n%s (FAIL %d / WARN %d)" %
              ("公開可" if not failed else "要修正", len(failed), len(warned)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
