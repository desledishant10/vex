# Vex architecture

This document describes Vex's internal design. Skim it if you're contributing
new attacks, detectors, or providers; read it fully if you want to understand
the framework's positioning vs. alternatives.

## Design principles

1. **Agent-first threat model.** Vex assumes the system under test ingests
   content the attacker can influence - emails, documents, RAG sources, tool
   outputs, MCP server responses. Probes are shaped accordingly.
2. **Stable probe content, forensic replay.** Given the same configuration, the
   same attack produces the same probe *content* in the same order (each probe
   is still stamped with a fresh random `id`; seeded byte-for-byte
   reproducibility is planned - issue #6). Raw provider responses are retained
   on every result for forensic replay.
3. **Provider-agnostic core.** The framework speaks in `Conversation` and
   `Message`. Providers translate at the network boundary. Adding a new
   provider is ~50 lines.
4. **Composable detectors.** Multiple detectors run on every response; the
   aggregate verdict is computed by a small, explicit rule (`VULNERABLE`
   dominates; `ERROR` next; `INCONCLUSIVE` next; `SAFE` is the floor).
5. **CI-native.** Stable JSON schema, `--exit-on-finding` gate, terse
   terminal output suitable for build logs.

## Component map

```
┌──────────────────────────────────────────────────────────────────┐
│                            vex.cli                               │
│                  (Typer entry points + UX)                       │
└──────────────────────────────┬───────────────────────────────────┘
                               │
              ┌────────────────┼──────────────────┐
              ▼                ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ vex.core         │ │ vex.attacks      │ │ vex.detectors    │
│  models          │ │  jailbreaks      │ │  refusal         │
│  attack (ABC)    │ │  prompt_injection│ │  pattern         │
│  target          │ │  agent_attacks   │ │  compliance      │
│  detector (ABC)  │ │  extraction (v2) │ │  llm_judge       │
│  orchestrator    │ │                  │ │                  │
└────────┬─────────┘ └────────┬─────────┘ └──────────┬───────┘
         │                    │                      │
         └────────────────────┼──────────────────────┘
                              ▼
                  ┌──────────────────────┐
                  │ vex.providers        │
                  │  base (ABC)          │
                  │  anthropic           │
                  │  openai (+compat)    │
                  │  ollama              │
                  └──────────────────────┘
                              ▼
                  ┌──────────────────────┐
                  │ vex.reports          │
                  │  terminal (rich)     │
                  │  json (stable)       │
                  │  html (self-contained│
                  └──────────────────────┘
```

## Data flow

1. CLI builds a `Target` from `--target provider:model`.
2. CLI selects `Attack` classes by ID or category filter and instantiates them.
3. `Orchestrator.run(attacks)`:
   - Each attack's `generate()` yields one or more `Probe` objects.
   - Probes are dispatched via a bounded asyncio semaphore (`--concurrency`).
   - Each probe's conversation is sent to the target via the provider's
     `complete()`. The text + raw response are stored on `ProbeResult`.
   - For each result, every registered `Detector.evaluate()` is awaited
     against the response. Findings accumulate on the result.
   - Aggregate `verdict` is computed from the findings.
4. `RunSummary` is returned with all `ProbeResult` objects.
5. Reports are rendered from the summary.

## Verdict aggregation

A `ProbeResult` exposes a single `verdict` derived from its findings via one of
three `VerdictMode` strategies (`--verdict-mode`):

- **`strictest`** - `VULNERABLE` if any finding is VULNERABLE, else ERROR, else
  INCONCLUSIVE, else SAFE. Conservative: it flags anything not clearly refused,
  so false-positive VULNERABLE is traded for never missing a finding.
- **`judge_priority`** - the LLM judge's verdict is authoritative at confidence
  >= 0.7, with one exception: it cannot overturn a high-confidence (>= 0.8)
  deterministic VULNERABLE such as a literal canary hit, so an injected target
  response cannot talk the judge into suppressing a finding it triggered. Falls
  back to `strictest` when no confident judge is present.
- **`majority_vote`** - confidence-weighted vote across all findings.

**Defaults:** `judge_priority` when a judge detector is in the stack,
`majority_vote` otherwise. The no-judge default is `majority_vote` (not
`strictest`) because the heuristic stack's inverted refusal detector emits a
low-confidence VULNERABLE on every non-refusal; under `strictest` that would
mark all non-refusals VULNERABLE, whereas confidence weighting lets the
stronger SAFE signals win.

**CI gating:** with `--exit-on-finding` the CLI exits 1 on any VULNERABLE and 3
when every probe errored (the target was never scanned); 0 otherwise.

## Extension points

### Adding an attack

1. Subclass `Attack` in a module under `src/vex/attacks/<category>/`.
2. Set class attributes: `id`, `category`, `severity`, `name`, `description`.
3. Implement `generate() -> Iterator[Probe]`. Use `self._make_probe(...)` for
   single-turn user probes or instantiate `Probe` directly for richer shapes.
4. Register the class in `src/vex/attacks/__init__.py` so `vex list` finds it.

### Adding a detector

1. Subclass `Detector` in a module under `src/vex/detectors/`.
2. Set `name`.
3. Implement `async def evaluate(self, probe, response) -> DetectorFinding`.
4. Detectors should be fast and side-effect-free; expensive judges should
   wrap a cheap target rather than block on synchronous compute.

### Adding a provider

1. Subclass `Provider` in `src/vex/providers/<name>.py`.
2. Set `name`.
3. Implement `async def complete(self, *, conversation, model, ...) -> tuple[str, dict]`.
4. Gate any SDK imports behind a try/except so users without the optional
   dependency see a helpful error.
5. Wire into `vex.cli._build_provider`.

## Stability guarantees

- **JSON report schema:** field names and types stable within a major version.
  New fields may be added; existing fields will not be removed or repurposed.
- **CLI flags:** subject to deprecation cycle (warn for one minor release
  before removal). Flags are part of the user contract.
- **`Attack` ID:** stable forever. Don't rename attack IDs; create a new ID
  and deprecate the old.
- **Python API (`from vex import ...`):** stable within a major version.

## Non-goals

- **Online red-teaming dashboard** - out of scope for v0.x. JSON output is
  designed for piping into existing security tooling.
- **Hosted service** - Vex is a library + CLI, not a SaaS. Hosting belongs
  to the user.
- **Automated jailbreak discovery via search/RL** - explicit v0.x non-goal.
  Bring your own LLM-guided fuzzing if you want this; the framework
  supports it via the plugin system.
