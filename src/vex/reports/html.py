"""HTML report - self-contained, styled, share-ready.

Single-file HTML with embedded CSS so a Vex report can be opened in any
browser, attached to an email, or hosted as a GitHub Pages artifact.
"""

from __future__ import annotations

import html
from collections.abc import Iterable
from pathlib import Path

from jinja2 import Environment, select_autoescape

from vex.core.models import RunSummary, Severity, Verdict

_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vex Scan - {{ summary.target }}</title>
<style>
  :root {
    --bg: #0b0e14;
    --panel: #131822;
    --fg: #e6e6e6;
    --muted: #8a92a6;
    --accent: #5ad3ff;
    --red: #ff6b6b;
    --green: #51cf66;
    --yellow: #ffd43b;
    --magenta: #cc66ff;
    --border: #1e2533;
  }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: var(--bg); color: var(--fg); margin: 0; padding: 2rem; line-height: 1.5; }
  h1, h2, h3 { margin: 0 0 0.5em; color: var(--accent); font-weight: 600; }
  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
           padding: 1.5rem; margin-bottom: 1.5rem; }
  .meta { display: grid; grid-template-columns: max-content 1fr; gap: 0.25rem 1rem; }
  .meta dt { color: var(--muted); }
  .stats { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; }
  .stat { text-align: center; padding: 1rem; border: 1px solid var(--border); border-radius: 8px; }
  .stat .num { font-size: 2rem; font-weight: 700; display: block; }
  .stat.vuln .num { color: var(--red); }
  .stat.safe .num { color: var(--green); }
  .stat.error .num { color: var(--magenta); }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); vertical-align: top; }
  th { color: var(--muted); font-weight: 500; font-size: 0.85rem;
       text-transform: uppercase; letter-spacing: 0.05em; }
  .sev { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem;
         font-weight: 700; text-transform: uppercase; }
  .sev.critical { background: #4a0000; color: var(--red); }
  .sev.high     { background: #3a1500; color: #ff9966; }
  .sev.medium   { background: #3a2c00; color: var(--yellow); }
  .sev.low      { background: #00333a; color: var(--accent); }
  .sev.info     { background: #2a2a2a; color: var(--muted); }
  details { background: #0e1219; border: 1px solid var(--border); border-radius: 6px;
            padding: 0.5rem 0.75rem; margin-top: 0.5rem; }
  details summary { cursor: pointer; color: var(--muted); font-size: 0.85rem; }
  pre { background: #08090d; padding: 0.75rem; border-radius: 6px; overflow-x: auto;
        font-size: 0.85rem; white-space: pre-wrap; word-break: break-word; }
  .footer { color: var(--muted); font-size: 0.8rem; text-align: center; margin-top: 2rem; }
</style>
</head>
<body>
  <h1>Vex Scan Report</h1>

  <div class="panel">
    <dl class="meta">
      <dt>Target</dt><dd>{{ summary.target }}</dd>
      <dt>Run ID</dt><dd>{{ summary.run_id }}</dd>
      <dt>Started</dt><dd>{{ summary.started_at }}</dd>
      {% if summary.finished_at %}<dt>Finished</dt><dd>{{ summary.finished_at }}</dd>{% endif %}
    </dl>
  </div>

  <div class="panel">
    <div class="stats">
      <div class="stat"><span class="num">{{ summary.total }}</span><span>Probes</span></div>
      <div class="stat vuln"><span class="num">{{ summary.vulnerable_count }}</span><span>Vulnerable</span></div>
      <div class="stat safe"><span class="num">{{ summary.safe_count }}</span><span>Safe</span></div>
      <div class="stat error"><span class="num">{{ summary.error_count }}</span><span>Errors</span></div>
      <div class="stat"><span class="num">{{ "%.1f"|format(summary.vulnerability_rate * 100) }}%</span><span>Vuln rate</span></div>
    </div>
  </div>

  <div class="panel">
    <h2>Findings by category</h2>
    <table>
      <thead><tr><th>Category</th><th>Total</th><th>Vulnerable</th><th>Safe</th><th>Errors</th></tr></thead>
      <tbody>
        {% for row in by_category %}
        <tr>
          <td>{{ row.category }}</td>
          <td>{{ row.total }}</td>
          <td>{{ row.vulnerable }}</td>
          <td>{{ row.safe }}</td>
          <td>{{ row.errors }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <div class="panel">
    <h2>Vulnerable probes</h2>
    {% if not vulnerable %}
      <p>No vulnerabilities found.</p>
    {% else %}
      <table>
        <thead><tr><th>Severity</th><th>Attack</th><th>Probe</th><th>Detector</th></tr></thead>
        <tbody>
          {% for v in vulnerable %}
          <tr>
            <td><span class="sev {{ v.severity }}">{{ v.severity }}</span></td>
            <td><code>{{ v.attack_id }}</code></td>
            <td>
              {{ v.title }}
              <details>
                <summary>Probe input</summary>
                <pre>{{ v.input }}</pre>
              </details>
              <details>
                <summary>Response</summary>
                <pre>{{ v.response }}</pre>
              </details>
              <details>
                <summary>Findings</summary>
                <pre>{{ v.findings }}</pre>
              </details>
            </td>
            <td>{{ v.detectors }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endif %}
  </div>

  <p class="footer">Generated by Vex {{ vex_version }} - github.com/desledishant10/vex</p>
</body>
</html>
"""


def _summarize_categories(summary: RunSummary) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for cat, results in sorted(summary.by_category().items(), key=lambda kv: kv[0].value):
        rows.append(
            {
                "category": cat.value,
                "total": len(results),
                "vulnerable": sum(1 for r in results if r.verdict == Verdict.VULNERABLE),
                "safe": sum(1 for r in results if r.verdict == Verdict.SAFE),
                "errors": sum(1 for r in results if r.verdict == Verdict.ERROR),
            }
        )
    return rows


def _summarize_vulnerable(summary: RunSummary) -> Iterable[dict[str, object]]:
    severity_order = list(Severity)
    vulnerable = [r for r in summary.results if r.verdict == Verdict.VULNERABLE]
    vulnerable.sort(key=lambda r: severity_order.index(r.probe.severity), reverse=True)
    for r in vulnerable:
        # Last user input is the actual probe content sent.
        user_input = ""
        for msg in reversed(r.probe.conversation.messages):
            if msg.role.value == "user":
                user_input = msg.content
                break
        detectors = ", ".join(f.detector for f in r.findings if f.verdict == Verdict.VULNERABLE)
        findings_dump = "\n".join(
            f"- [{f.detector}] {f.verdict.value} ({f.confidence:.2f}) - {f.rationale}"
            for f in r.findings
        )
        yield {
            "severity": r.probe.severity.value,
            "attack_id": r.probe.attack_id,
            "title": r.probe.title,
            "input": user_input,
            "response": r.response or "",
            "findings": findings_dump,
            "detectors": detectors,
        }


def render_html(summary: RunSummary, *, vex_version: str = "0.1.0") -> str:
    """Render the summary as a single-file HTML report."""
    env = Environment(autoescape=select_autoescape(["html"]))
    template = env.from_string(_TEMPLATE)
    return template.render(
        summary=summary,
        by_category=_summarize_categories(summary),
        vulnerable=list(_summarize_vulnerable(summary)),
        vex_version=vex_version,
        html=html,
    )


def write_html(summary: RunSummary, path: Path | str, *, vex_version: str = "0.1.0") -> Path:
    """Write the HTML report to ``path`` and return the path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_html(summary, vex_version=vex_version), encoding="utf-8")
    return target
