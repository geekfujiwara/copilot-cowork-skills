#!/usr/bin/env python3
"""CSV・JSON・XLSX のイベントデータから KPI を集計する（標準ライブラリのみ）。"""
from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

XML_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
OFFICE_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
TRUE_VALUES = {"true", "yes", "y", "1", "はい", "参加", "出席"}
FALSE_VALUES = {"false", "no", "n", "0", "いいえ", "不参加", "欠席", ""}


def load_json(path: Path) -> list[dict[str, object]]:
    obj = json.loads(path.read_text(encoding="utf-8"), strict=False)
    if isinstance(obj, dict) and isinstance(obj.get("result"), dict):
        obj = json.loads(obj["result"]["content"][0]["text"], strict=False)
    if isinstance(obj, dict) and isinstance(obj.get("value"), list):
        obj = obj["value"]
    if not isinstance(obj, list):
        raise ValueError(f"JSON配列またはvalue配列ではありません: {path}")
    return [item.get("fields", item) for item in obj if isinstance(item, dict)]


def load_csv(path: Path) -> list[dict[str, object]]:
    raw = path.read_text(encoding="utf-8-sig")
    try:
        dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",\t;")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(raw.splitlines(), dialect=dialect))


def column_index(cell_reference: str) -> int:
    letters = re.match(r"[A-Z]+", cell_reference.upper())
    if not letters:
        return 0
    value = 0
    for letter in letters.group(0):
        value = value * 26 + ord(letter) - ord("A") + 1
    return value - 1


def load_xlsx(path: Path, sheet_name: str | None) -> list[dict[str, object]]:
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", XML_NS):
                shared.append("".join(node.text or "" for node in item.iterfind(".//m:t", XML_NS)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
        sheets = workbook.find("m:sheets", XML_NS)
        if sheets is None:
            return []
        selected = None
        for sheet in sheets:
            if sheet_name is None or sheet.attrib.get("name") == sheet_name:
                selected = sheet
                break
        if selected is None:
            raise ValueError(f"ワークシートが見つかりません: {sheet_name}")
        target = targets[selected.attrib[OFFICE_REL]].lstrip("/")
        worksheet_path = target if target.startswith("xl/") else f"xl/{target}"
        root = ET.fromstring(archive.read(worksheet_path))

        matrix: list[list[object]] = []
        for row in root.findall(".//m:sheetData/m:row", XML_NS):
            values: list[object] = []
            for cell in row.findall("m:c", XML_NS):
                index = column_index(cell.attrib.get("r", "A1"))
                while len(values) <= index:
                    values.append("")
                value_node = cell.find("m:v", XML_NS)
                value: object = "" if value_node is None else value_node.text or ""
                if cell.attrib.get("t") == "s" and value != "":
                    value = shared[int(str(value))]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(node.text or "" for node in cell.iterfind(".//m:t", XML_NS))
                values[index] = value
            matrix.append(values)
    if not matrix:
        return []
    headers = [str(value).strip() for value in matrix[0]]
    return [
        {header: row[index] if index < len(row) else "" for index, header in enumerate(headers) if header}
        for row in matrix[1:]
        if any(str(value).strip() for value in row)
    ]


def load_records(path: str, sheet_name: str | None = None) -> list[dict[str, object]]:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".json":
        return load_json(source)
    if suffix in {".csv", ".tsv"}:
        return load_csv(source)
    if suffix == ".xlsx":
        return load_xlsx(source, sheet_name)
    raise ValueError(f"未対応の形式です（JSON/CSV/TSV/XLSXのみ）: {source}")


def boolean_value(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    normalized = str(value or "").strip().casefold()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    return None


def normalize_company(value: object) -> str:
    name = str(value or "").strip()
    for suffix in ("株式会社", "(株)", "（株）", "合同会社", "有限会社"):
        name = name.replace(suffix, "")
    return name.replace("　", "").replace(" ", "").strip()


def aggregate(rows: list[dict[str, object]], args: argparse.Namespace) -> dict[str, object]:
    result: dict[str, object] = {"total_records": len(rows)}
    data = rows
    if args.attend_field:
        states = [boolean_value(row.get(args.attend_field)) for row in rows]
        data = [row for row, state in zip(rows, states) if state is True]
        result.update(attending=len(data), not_attending=states.count(False), unknown_attendance=states.count(None))
    for field in args.choice_fields:
        counts = Counter(str(row.get(field) or "(未設定)") for row in data)
        result[f"dist_{field}"] = dict(counts.most_common())
    for field in args.bool_fields:
        states = [boolean_value(row.get(field)) for row in data]
        yes = states.count(True)
        no = states.count(False)
        result[f"bool_{field}"] = {
            "true": yes, "false": no, "unknown": states.count(None),
            "rate": round(yes / (yes + no), 3) if yes + no else 0,
        }
    if args.company_field:
        companies = [normalize_company(row.get(args.company_field)) for row in data]
        counts = Counter(value for value in companies if value)
        result["companies"] = {"unique_normalized": len(counts), "top": dict(counts.most_common(20))}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", nargs="+", required=True)
    parser.add_argument("--sheet")
    parser.add_argument("--attend-field")
    parser.add_argument("--choice-fields", nargs="*", default=[])
    parser.add_argument("--bool-fields", nargs="*", default=[])
    parser.add_argument("--company-field")
    parser.add_argument("--out")
    args = parser.parse_args()
    rows = [row for path in args.files for row in load_records(path, args.sheet)]
    output = json.dumps(aggregate(rows, args), ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        print(f"WROTE: {args.out}")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
