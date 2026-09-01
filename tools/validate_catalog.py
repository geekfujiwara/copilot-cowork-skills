#!/usr/bin/env python3
"""公開前にスキルカタログの構造・秘匿性・安全ガードを検証する。"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED_ROOT_FILES = {
    "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "catalog/skills.json",
}
ALLOWED_CATEGORIES = {
    "productivity", "communication", "analysis", "writing", "research",
    "automation", "custom",
}
ALLOWED_URL_HOSTS = {
    "example.com", "teams.microsoft.com", "graph.microsoft.com",
    "www.google.com", "transit.yahoo.co.jp", "github.com", "x.com",
    "img.shields.io", "schemas.openxmlformats.org",
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt"}
RISKY_BINARY_SUFFIXES = {".exe", ".dll", ".ttf", ".ttc", ".otf", ".woff", ".woff2"}
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
GUID_RE = re.compile(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", re.I)
SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|client[_-]?secret|password|access[_-]?token)\b\s*[:=]\s*[\"']?([^\s\"']+)"
)
ABS_PATH_RE = re.compile(r"(?:\b[A-Za-z]:\\(?:Users|Documents|dev)\\|/(?:home|Users)/[^\s/]+/)")
STEP_RE = re.compile(r"^###\s+(?:Step|Phase)\s+(\d+)\s*[:：.]", re.M | re.I)
URL_RE = re.compile(r"https?://[^\s)`>\"]+")
SEND_RE = re.compile(r"SendEmail|SendDraftMessage|PostMessage|SendMessage", re.I)
SEND_GUARD_RE = re.compile(r"明示.{0,20}(?:依頼|指示|確認|承認)|(?:確認|承認).{0,20}(?:送信|投稿)|explicit|confirm", re.I | re.S)
BYPASS_RE = re.compile(
    r"ガード.{0,12}(?:回避|迂回)(?!しな)|承認.{0,12}(?:不要|省略)(?!しな)|プレビュー.{0,12}なし",
    re.I | re.S,
)
CATALOG_REF_RE = re.compile(r"`catalog:([a-z0-9]+(?:-[a-z0-9]+)*)`")
COMPONENT_REF_RE = re.compile(r"(?<![A-Za-z0-9_.-])((?:references|scripts)/[A-Za-z0-9_.-]+)")
MARKDOWN_LINK_RE = re.compile(r"\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)")
NAMED_EXTERNAL_SKILL_RE = re.compile(
    r"`([a-z][a-z0-9-]*)`\s*(?:スキル|skill)\b|\b([a-z][a-z0-9]*-[a-z0-9-]+)\s+(?:スキル|skill)\b",
    re.I,
)
README_TABLE_BEGIN = "<!-- BEGIN GENERATED SKILL TABLE -->"
README_TABLE_END = "<!-- END GENERATED SKILL TABLE -->"
CATEGORY_LABELS = {
    "productivity": "生産性",
    "communication": "コミュニケーション",
    "analysis": "分析",
    "writing": "文書作成",
    "research": "調査",
    "automation": "自動化",
    "custom": "カスタム",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str | None:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    return match.group(1) if match else None


def scalar(fm: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*([^|>\n][^\n]*)$", fm, re.M)
    return match.group(1).strip().strip("\"'") if match else None


def list_items(fm: str, key: str) -> list[str]:
    match = re.search(rf"^{re.escape(key)}:\s*\n((?:\s+-\s+[^\n]+\n?)+)", fm, re.M)
    return re.findall(r"^\s+-\s+(.+)$", match.group(1), re.M) if match else []


def nested_scalar(fm: str, parent: str, key: str) -> str | None:
    match = re.search(
        rf"^{re.escape(parent)}:\s*\n(?P<body>(?:[ \t]+[^\n]*\n?)+)", fm, re.M
    )
    if not match:
        return None
    value = re.search(rf"^[ \t]+{re.escape(key)}:\s*([^\n]+)$", match.group("body"), re.M)
    return value.group(1).strip().strip("\"'") if value else None


def block_scalar(fm: str, key: str) -> str | None:
    match = re.search(
        rf"^{re.escape(key)}:\s*[|>][-+]?\s*\n(?P<body>(?:[ \t]+[^\n]*(?:\n|$))+)",
        fm,
        re.M,
    )
    if not match:
        return None
    lines = [line.strip() for line in match.group("body").splitlines()]
    return " ".join(line for line in lines if line)


def skill_metadata(skill: Path) -> dict[str, object]:
    text = read_text(skill / "SKILL.md")
    fm = frontmatter(text) or ""
    source_paths = [skill / "SKILL.md"]
    references = skill / "references"
    if references.is_dir():
        source_paths.extend(sorted(references.glob("*.md")))
    source_text = "\n".join(read_text(path) for path in source_paths)
    return {
        "name": scalar(fm, "name") or skill.name,
        "category": scalar(fm, "category") or "",
        "description": block_scalar(fm, "description") or "",
        "triggers": list_items(fm, "triggers"),
        "dependencies": {
            "capabilities": list_items(fm, "capabilities"),
            "skills": sorted(set(CATALOG_REF_RE.findall(source_text))),
            "components": sorted(set(COMPONENT_REF_RE.findall(source_text))),
        },
    }


def catalog_data() -> dict[str, object]:
    skills = [
        skill_metadata(path)
        for path in sorted(SKILLS.iterdir())
        if path.is_dir()
    ]
    return {"schema_version": 1, "skills": skills}


def render_catalog_json() -> str:
    return json.dumps(catalog_data(), ensure_ascii=False, indent=2) + "\n"


def render_readme_table() -> str:
    rows = ["| 領域 | スキル | 概要 | 依存先 |", "|---|---|---|---|"]
    skills = catalog_data()["skills"]
    assert isinstance(skills, list)
    for item in sorted(skills, key=lambda value: (str(value["category"]), str(value["name"]))):
        dependencies = item["dependencies"]
        assert isinstance(dependencies, dict)
        capabilities = [str(value) for value in dependencies["capabilities"]]
        skill_refs = [f"`catalog:{value}`" for value in dependencies["skills"]]
        dependency_text = " / ".join(capabilities + skill_refs) or "なし"
        description = str(item["description"]).split("。", 1)[0] + "。"
        description = description.replace("|", "\\|")
        rows.append(
            f"| {CATEGORY_LABELS.get(str(item['category']), str(item['category']))} "
            f"| `{item['name']}` | {description} | {dependency_text} |"
        )
    return "\n".join(rows)


def replace_generated_readme_table(readme: str) -> str:
    pattern = re.compile(
        rf"{re.escape(README_TABLE_BEGIN)}.*?{re.escape(README_TABLE_END)}",
        re.S,
    )
    replacement = f"{README_TABLE_BEGIN}\n{render_readme_table()}\n{README_TABLE_END}"
    updated, count = pattern.subn(lambda _: replacement, readme)
    if count != 1:
        raise ValueError("README.md の生成テーブルマーカーが1組ではありません")
    return updated


def generated_file_errors() -> list[str]:
    errors: list[str] = []
    catalog_path = ROOT / "catalog" / "skills.json"
    if not catalog_path.is_file() or read_text(catalog_path) != render_catalog_json():
        errors.append("catalog/skills.json が最新ではありません: python -B tools/sync_catalog.py")
    readme_path = ROOT / "README.md"
    try:
        expected_readme = replace_generated_readme_table(read_text(readme_path))
    except (OSError, ValueError) as exc:
        errors.append(f"README.md の生成領域を検証できません: {exc}")
    else:
        if read_text(readme_path) != expected_readme:
            errors.append("README.md のスキル一覧が最新ではありません: python -B tools/sync_catalog.py")
    return errors


def validate_references(skill: Path, skill_names: set[str]) -> list[str]:
    """他スキルと同梱コンポーネントへの参照が解決できることを検証する。"""
    errors: list[str] = []
    text_paths = [skill / "SKILL.md"]
    references = skill / "references"
    if references.is_dir():
        text_paths.extend(sorted(references.glob("*.md")))

    for path in text_paths:
        if not path.is_file():
            continue
        text = read_text(path)
        rel = path.relative_to(ROOT).as_posix()

        for target in CATALOG_REF_RE.findall(text):
            if target not in skill_names:
                errors.append(f"{rel}: 未解決のカタログスキル参照です: catalog:{target}")
            elif target == skill.name:
                errors.append(f"{rel}: 自分自身へのカタログ参照です: catalog:{target}")

        for other in sorted(skill_names - {skill.name}):
            raw_ref = re.compile(rf"(?<!catalog:)`{re.escape(other)}`")
            if raw_ref.search(text):
                errors.append(
                    f"{rel}: ローカルスキル参照は `catalog:{other}` と明記してください"
                )

        for match in NAMED_EXTERNAL_SKILL_RE.finditer(text):
            target = next(group for group in match.groups() if group)
            if target.lower() not in {"catalog", "custom"}:
                errors.append(
                    f"{rel}: 未宣言の名前付きスキル参照です: {target}. "
                    "同梱スキルは `catalog:<name>`、外部機能は一般的な機能名で記載してください"
                )

        for component in COMPONENT_REF_RE.findall(text):
            target = skill / component
            if not target.is_file():
                errors.append(f"{rel}: 同梱コンポーネント参照が見つかりません: {component}")

        for link in MARKDOWN_LINK_RE.findall(text):
            if link in {"...", "…"} or "<" in link or "{" in link:
                continue
            target = (path.parent / link).resolve()
            try:
                target.relative_to(skill.resolve())
            except ValueError:
                errors.append(f"{rel}: スキル外への相対リンクは禁止です: {link}")
                continue
            if not target.is_file():
                errors.append(f"{rel}: Markdown リンクが見つかりません: {link}")
    return errors


def validate_skill(skill: Path, skill_names: set[str]) -> list[str]:
    errors: list[str] = []
    doc = skill / "SKILL.md"
    rel = doc.relative_to(ROOT).as_posix()
    if not doc.is_file():
        return [f"{skill.name}: SKILL.md がありません"]

    text = read_text(doc)
    fm = frontmatter(text)
    if fm is None:
        return [f"{rel}: YAML frontmatter がありません"]

    name = scalar(fm, "name")
    category = scalar(fm, "category")
    triggers = list_items(fm, "triggers")
    capabilities = list_items(fm, "capabilities")
    cowork_category = nested_scalar(fm, "cowork", "category")
    cowork_icon = nested_scalar(fm, "cowork", "icon")
    if name != skill.name:
        errors.append(f"{rel}: name ({name!r}) とフォルダー名が一致しません")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill.name):
        errors.append(f"{rel}: フォルダー名は kebab-case にしてください")
    if category not in ALLOWED_CATEGORIES:
        errors.append(f"{rel}: category が未設定または不正です")
    if len(triggers) < 3:
        errors.append(f"{rel}: triggers を 3 件以上設定してください")
    if not capabilities:
        errors.append(f"{rel}: capabilities を 1 件以上設定してください")
    if cowork_category != category:
        errors.append(f"{rel}: cowork.category と category を一致させてください")
    if not cowork_icon:
        errors.append(f"{rel}: cowork.icon がありません")

    steps = [int(n) for n in STEP_RE.findall(text)]
    if not steps:
        errors.append(f"{rel}: `### Step 1:` 形式の正常系 Step がありません")
    elif steps != list(range(1, len(steps) + 1)):
        errors.append(f"{rel}: Step 番号が連番ではありません: {steps}")

    referenced = set(PLACEHOLDER_RE.findall(text))
    unknown = sorted(referenced - {"N", "ABS_PATH_TO_PPTX"})
    if unknown:
        errors.append(f"{rel}: 未定義プレースホルダー: {', '.join(unknown)}")

    if SEND_RE.search(text) and not SEND_GUARD_RE.search(text):
        errors.append(f"{rel}: 送信・投稿処理に明示的な確認ガードがありません")
    if BYPASS_RE.search(text):
        errors.append(f"{rel}: ガードまたは承認を回避する指示があります")

    refs = skill / "references"
    if not refs.is_dir() or not (refs / "troubleshooting.md").is_file():
        errors.append(f"{rel}: references/troubleshooting.md がありません")
    errors.extend(validate_references(skill, skill_names))
    return errors


def validate_repository() -> list[str]:
    errors: list[str] = []
    for filename in sorted(REQUIRED_ROOT_FILES):
        if not (ROOT / filename).is_file():
            errors.append(f"{filename}: 必須ファイルがありません")

    if not SKILLS.is_dir():
        return errors + ["skills/: ディレクトリがありません"]
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    skill_names = {path.name for path in skill_dirs}
    for skill in skill_dirs:
        errors.extend(validate_skill(skill, skill_names))
    errors.extend(generated_file_errors())

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "build" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in RISKY_BINARY_SUFFIXES:
            errors.append(f"{rel}: 再配布条件を確認しにくいバイナリを同梱しないでください")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "LICENSE":
            continue
        text = read_text(path)
        if path.suffix.lower() == ".py":
            try:
                ast.parse(text, filename=rel)
            except SyntaxError as exc:
                errors.append(f"{rel}:{exc.lineno}: Python 構文エラー: {exc.msg}")
        for line_no, line in enumerate(text.splitlines(), 1):
            for email in EMAIL_RE.findall(line):
                if email.lower() != "you@example.com":
                    errors.append(f"{rel}:{line_no}: 実メールアドレスらしき値があります")
            for guid in GUID_RE.findall(line):
                if guid != "00000000-0000-0000-0000-000000000000":
                    errors.append(f"{rel}:{line_no}: 実 GUID らしき値があります")
            secret = SECRET_RE.search(line)
            if secret and secret.group(2) not in {"<value>", "CHANGE_ME", "example"}:
                errors.append(f"{rel}:{line_no}: シークレットらしき値があります")
            if ABS_PATH_RE.search(line):
                errors.append(f"{rel}:{line_no}: 個人環境の絶対パスらしき値があります")
            for raw_url in URL_RE.findall(line):
                host = (urlparse(raw_url).hostname or "").lower()
                if host and host not in ALLOWED_URL_HOSTS:
                    errors.append(f"{rel}:{line_no}: 未許可の URL ホストです: {host}")
    return errors


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    errors = validate_repository()
    if errors:
        print(f"FAIL: {len(errors)} 件")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {len(list(SKILLS.iterdir()))} skills validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
