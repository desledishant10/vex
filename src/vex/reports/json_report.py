"""JSON report - the canonical machine-readable Vex output.

Optimized for CI consumption and downstream tooling. Field names are stable
across versions; new fields may be added but existing ones won't be removed
within a major version.
"""

from __future__ import annotations

import json
from pathlib import Path

from vex.core.models import RunSummary


def render_json(summary: RunSummary, *, pretty: bool = True) -> str:
    """Serialize a :class:`RunSummary` to a JSON string."""
    data = summary.model_dump(mode="json")
    data["meta"] = {
        "total": summary.total,
        "vulnerable_count": summary.vulnerable_count,
        "safe_count": summary.safe_count,
        "error_count": summary.error_count,
        "vulnerability_rate": summary.vulnerability_rate,
    }
    if pretty:
        return json.dumps(data, indent=2, sort_keys=False, default=str)
    return json.dumps(data, default=str)


def write_json(summary: RunSummary, path: Path | str, *, pretty: bool = True) -> Path:
    """Write the JSON report to ``path`` and return the path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_json(summary, pretty=pretty), encoding="utf-8")
    return target
