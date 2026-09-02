#!/usr/bin/env python3
"""Profile CSV, TSV, JSON, or XLSX records without changing source data."""
from __future__ import annotations
import argparse, csv, json, math, statistics
from collections import Counter
from pathlib import Path
from typing import Any

def load_records(path: str, sheet: str | None = None) -> list[dict[str, Any]]:
    source, suffix = Path(path), Path(path).suffix.lower()
    if suffix == ".json":
        value = json.loads(source.read_text(encoding="utf-8-sig"))
        if isinstance(value, dict) and isinstance(value.get("value"), list): value = value["value"]
        if not isinstance(value, list): raise ValueError("JSON配列またはvalue配列が必要です")
        return [item for item in value if isinstance(item, dict)]
    if suffix in {".csv", ".tsv"}:
        text = source.read_text(encoding="utf-8-sig"); delimiter = "\t" if suffix == ".tsv" else ","
        try: delimiter = csv.Sniffer().sniff(text[:4096], delimiters=",\t;").delimiter
        except csv.Error: pass
        return list(csv.DictReader(text.splitlines(), delimiter=delimiter))
    if suffix == ".xlsx":
        import openpyxl
        book = openpyxl.load_workbook(source, read_only=True, data_only=True); ws = book[sheet] if sheet else book.worksheets[0]
        rows = ws.iter_rows(values_only=True); headers = [str(v).strip() if v is not None else "" for v in next(rows)]
        return [{h: row[i] if i < len(row) else None for i, h in enumerate(headers) if h} for row in rows if any(v not in (None, "") for v in row)]
    raise ValueError(f"未対応形式です: {suffix}")

def number(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""): return None
    try:
        result = float(str(value).replace(",", "").strip()); return result if math.isfinite(result) else None
    except ValueError: return None

def profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    columns = sorted({key for row in rows for key in row}); output: dict[str, Any] = {"row_count": len(rows), "column_count": len(columns), "columns": {}}
    for column in columns:
        values = [row.get(column) for row in rows]; present = [v for v in values if v not in (None, "")]; numeric = [v for v in (number(x) for x in present) if v is not None]
        info: dict[str, Any] = {"present": len(present), "missing": len(values)-len(present), "unique": len({str(v) for v in present}), "top_values": dict(Counter(str(v) for v in present).most_common(10))}
        if numeric and len(numeric) >= max(1, len(present)//2): info["numeric"] = {"count": len(numeric), "min": min(numeric), "max": max(numeric), "mean": statistics.fmean(numeric), "median": statistics.median(numeric)}
        output["columns"][column] = info
    return output

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("files", nargs="+"); parser.add_argument("--sheet"); parser.add_argument("--out"); args = parser.parse_args()
    rendered = json.dumps({p: profile(load_records(p, args.sheet)) for p in args.files}, ensure_ascii=False, indent=2, default=str)+"\n"
    if args.out: Path(args.out).write_text(rendered, encoding="utf-8"); print(f"WROTE: {args.out}")
    else: print(rendered, end="")
    return 0
if __name__ == "__main__": raise SystemExit(main())
