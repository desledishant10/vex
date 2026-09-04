"""Terminal report - rich-text summary printed at end of a scan."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from vex.core.models import RunSummary, Severity, Verdict

_VERDICT_STYLE = {
    Verdict.VULNERABLE: "bold red",
    Verdict.SAFE: "green",
    Verdict.INCONCLUSIVE: "yellow",
    Verdict.ERROR: "magenta",
}

_SEVERITY_STYLE = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "cyan",
    Severity.INFO: "dim",
}


def render_terminal(summary: RunSummary, *, console: Console | None = None) -> None:
    """Pretty-print the run summary to the terminal."""
    console = console or Console()

    header = Text()
    header.append("Vex Scan Report\n", style="bold cyan")
    header.append("Target:  ", style="dim")
    header.append(f"{summary.target}\n")
    header.append("Run ID:  ", style="dim")
    header.append(f"{summary.run_id}\n")
    if summary.finished_at:
        duration = (summary.finished_at - summary.started_at).total_seconds()
        header.append("Elapsed: ", style="dim")
        header.append(f"{duration:.1f}s\n")
    console.print(Panel(header, expand=False))

    # Top-line stats.
    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="dim")
    stats.add_column()
    stats.add_row("Probes run:", str(summary.total))
    stats.add_row(
        "Vulnerable:",
        Text(str(summary.vulnerable_count), style=_VERDICT_STYLE[Verdict.VULNERABLE]),
    )
    stats.add_row(
        "Safe:",
        Text(str(summary.safe_count), style=_VERDICT_STYLE[Verdict.SAFE]),
    )
    if summary.error_count:
        stats.add_row(
            "Errors:",
            Text(str(summary.error_count), style=_VERDICT_STYLE[Verdict.ERROR]),
        )
    stats.add_row(
        "Vuln rate:",
        Text(f"{summary.vulnerability_rate * 100:.1f}%", style="bold"),
    )
    console.print(stats)
    console.print()

    # Findings by category.
    by_cat = summary.by_category()
    if by_cat:
        table = Table(title="Findings by Category", expand=False)
        table.add_column("Category")
        table.add_column("Total", justify="right")
        table.add_column("Vulnerable", justify="right", style="red")
        table.add_column("Safe", justify="right", style="green")
        table.add_column("Errors", justify="right", style="magenta")
        for category, results in sorted(by_cat.items(), key=lambda kv: kv[0].value):
            v = sum(1 for r in results if r.verdict == Verdict.VULNERABLE)
            s = sum(1 for r in results if r.verdict == Verdict.SAFE)
            e = sum(1 for r in results if r.verdict == Verdict.ERROR)
            table.add_row(category.value, str(len(results)), str(v), str(s), str(e))
        console.print(table)
        console.print()

    # Vulnerable findings detail.
    vulnerable_results = [r for r in summary.results if r.verdict == Verdict.VULNERABLE]
    if vulnerable_results:
        table = Table(title="Vulnerable Probes", expand=True, show_lines=True)
        table.add_column("Severity", no_wrap=True)
        table.add_column("Attack")
        table.add_column("Probe")
        table.add_column("Detector(s)")
        for r in sorted(
            vulnerable_results,
            key=lambda x: list(Severity).index(x.probe.severity),
            reverse=True,
        ):
            sev = Text(r.probe.severity.value.upper(), style=_SEVERITY_STYLE[r.probe.severity])
            detectors = ", ".join(f.detector for f in r.findings if f.verdict == Verdict.VULNERABLE)
            table.add_row(sev, r.probe.attack_id, r.probe.title, detectors)
        console.print(table)
    elif summary.error_count == summary.total and summary.total > 0:
        console.print(
            Text(
                f"All {summary.total} probes errored - no results. "
                "Check the target spec, API key, and network.",
                style="bold red",
            )
        )
    elif summary.error_count:
        console.print(
            Text(
                f"No vulnerabilities found, but {summary.error_count} of "
                f"{summary.total} probes errored (results incomplete).",
                style="bold yellow",
            )
        )
    else:
        console.print(Text("No vulnerabilities found.", style="bold green"))
