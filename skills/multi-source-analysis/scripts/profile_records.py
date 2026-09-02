#!/usr/bin/env python3
"""Profile records in CSV, TSV, JSON, or XLSX files without changing source data."""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


def load_records(path: str, sheet: str | None = None) -> list[dict[str, Any]]:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".json":
        value = json.loads(source.read_text(encoding="utf-8-sig"))
        if isinstance(value, dict) and isinstance(value.get("value"), list):
            value = value["value"]
        if not isinstance(value, list):
            raise ValueError("JSONはオブジェクト配列またはvalue配列である必要があります")
        return [item for item in value if isinstance(item, dict)]
    if suffix in {".csv", ".tsv"}:
        text = source.read_text(encoding="utf-8-sig")
        delimiter = "\t" if suffix == ".tsv" else ","
        try:
            dialect = csv.Sniffer().sniff(text[:4096], delimiters=",\t;")
            delimiter = dialect.delimiter
        except csv.Error:
            pass
        return list(csv.DictReader(text.splitlines(), delimiter=delimiter))
    if suffix == ".xlsx":
        try:
            import openpyxl
        except ImportError as exc:
            raise RuntimeError("XLSXにはopenpyxlが必要です") from exc
        workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
        worksheet = workbook[sheet] if sheet else workbook.worksheets[0]
        rows = worksheet.iter_rows(values_only=True)
        headers = [str(value).strip() if value is not None else "" for value in next(rows)]
        return [
            {header: row[index] if index < len(row) else None for index, header in enumerate(headers) if header}
            for row in rows
            if any(value not in (None, "") for value in row)
        ]
    raise ValueError(f"未対応形式です: {suffix}")


def number(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        result = float(str(value).replace(",", "").strip())
        return result if math.isfinite(result) else None
    except ValueError:
        return None


def profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    columns = sorted({key for row in rows for key in row})
    output: dict[str, Any] = {"row_count": len(rows), "column_count": len(columns), "columns": {}}
    for column in columns:
        values = [row.get(column) for row in rows]
        present = [value for value in values if value not in (None, "")]
        numeric = [value for value in (number(item) for item in present) if value is not None]
        info: dict[str, Any] = {
            "present": len(present),
            "missing": len(values) - len(present),
            "unique": len({str(value) for value in present}),
            "top_values": dict(Counter(str(value) for value in present).most_common(10)),
        }
        if numeric and len(numeric) >= max(1, len(present) // 2):
            info["numeric"] = {
                "count": len(numeric),
                "min": min(numeric),
                "max": max(numeric),
                "mean": statistics.fmean(numeric),
                "median": statistics.median(numeric),
            }
        output["columns"][column] = info
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--sheet")
    parser.add_argument("--out")
    args = parser.parse_args()
    result = {path: profile(load_records(path, args.sheet)) for path in args.files}
    rendered = json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n"
    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
        print(f"WROTE: {args.out}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
