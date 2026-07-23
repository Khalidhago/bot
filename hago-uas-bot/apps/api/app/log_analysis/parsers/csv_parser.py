"""CSV/JSON telemetry parser (generic format)."""

from __future__ import annotations

import csv
import io
import json
from typing import Any


def parse_csv(content: bytes) -> dict[str, Any]:
    """Parse a generic CSV telemetry file into a structured dict."""
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        return {}

    # Extract basic stats from common column names
    result: dict[str, Any] = {"row_count": len(rows), "columns": list(rows[0].keys())}

    def _col_min_max(col: str) -> tuple[float | None, float | None]:
        vals = []
        for row in rows:
            try:
                vals.append(float(row.get(col, "")))
            except (ValueError, TypeError):
                pass
        return (min(vals), max(vals)) if vals else (None, None)

    # Battery voltage
    for col in ("voltage", "Volt", "BAT_VOLT", "battery_voltage", "VoltVFilt"):
        if col in (rows[0] if rows else {}):
            vmin, vmax = _col_min_max(col)
            if vmin is not None:
                result["battery"] = {"voltage_min_v": vmin, "voltage_max_v": vmax}
            break

    # GPS
    for col in ("fix_type", "GPS_FIX", "fixType"):
        if col in (rows[0] if rows else {}):
            fixes = []
            for row in rows:
                try:
                    fixes.append(int(row[col]))
                except (ValueError, TypeError):
                    pass
            if fixes:
                result["gps"] = {"fix_type": min(fixes), "hdop": None}
            break

    return result


def parse_json_telemetry(content: bytes) -> dict[str, Any]:
    """Parse a JSON telemetry file."""
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {"records": data, "row_count": len(data)}
        return {"raw": data}
    except json.JSONDecodeError as exc:
        return {"parse_error": str(exc)}
