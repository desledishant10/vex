"""Render a Vex run's terminal report to an SVG for embedding in docs/README.

Uses Rich's recording mode to capture the same terminal output `vex scan`
produces — but as a static SVG that renders identically on every viewer.

Usage::

    python scripts/make_demo_svg.py runs/baseline-v02/results.json docs/assets/cli-demo.svg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console

from vex.core.models import RunSummary
from vex.reports.terminal import render_terminal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_json", type=Path)
    parser.add_argument("output_svg", type=Path)
    parser.add_argument("--title", default="vex scan", help="Title shown in the SVG window-chrome.")
    parser.add_argument("--width", type=int, default=120, help="Console width in characters.")
    args = parser.parse_args()

    if not args.results_json.exists():
        print(f"Not found: {args.results_json}", file=sys.stderr)
        return 2

    data = json.loads(args.results_json.read_text(encoding="utf-8"))
    # The RunSummary computed_field for verdict requires real ProbeResult
    # objects; load with model_validate to handle datetime coercion.
    # We do this through json round-trip for safety with the file's iso
    # datetime strings.
    summary = RunSummary.model_validate(data)

    console = Console(record=True, width=args.width)
    render_terminal(summary, console=console)
    console.print()
    console.print(
        "[dim]JSON report: runs/baseline-v02/results.json[/]\n"
        "[dim]HTML report: runs/baseline-v02/results.html[/]"
    )

    args.output_svg.parent.mkdir(parents=True, exist_ok=True)
    console.save_svg(str(args.output_svg), title=args.title)

    print(f"Wrote {args.output_svg} ({args.output_svg.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
