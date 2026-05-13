# Changelog

All notable changes to Vex are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.3
- MCP server target adapter — probe servers exposing tools to agents
- Browser-agent attack module (Claude Computer Use, OpenAI Operator)
- Multi-turn crescendo attack family
- Cross-session memory poisoning probes
- Entry-point-based plugin discovery (`vex.attacks` group)
- Reproducibility seeds for stochastic attacks

## [0.2.0] — 2026-05-13

Detector calibration release. Reduces false-positive rate on frontier models
from ~60% to ~0% based on replay of the v0.1 baseline run against
`claude-sonnet-4-6` (12/18 false positives → 0/18, with the 1 real
vulnerability still correctly flagged).

### Added
- **`VerdictMode` enum** (#14) — three aggregation strategies for detector
  findings:
  - `STRICTEST` (v0.1 default, still available): any VULNERABLE wins
  - `JUDGE_PRIORITY` (new v0.2 default when judge present): LLM-judge verdict
    is authoritative at confidence ≥ 0.7
  - `MAJORITY_VOTE`: confidence-weighted vote across all detectors
- **`--verdict-mode` CLI flag** — explicit override of the auto-selected mode
- **Context-aware mode for `PatternDetector`** (#13) — new `context_aware=True`
  parameter classifies the ±250-char window around each canary hit as
  "warning" vs. "compliance" context. Eliminates the false-positive class
  where the model detected and quoted the canary in a security warning.
  Falls back to a canary-density heuristic (≥30% of response → compliance)
  when surrounding context is neutral.
- **Modernized refusal patterns** (#12) — three-tier pattern library:
  - Tier 1: classic English boilerplate ("I cannot help") — 0.9 confidence
  - Tier 2: modern conversational refusals ("I don't have a system prompt",
    "I'm still Claude", "I appreciate the creative framing", "This is a
    social engineering attempt") — 0.7–0.85 confidence
  - Tier 3: non-English refusals (French, Spanish, German, Italian,
    Portuguese, Mandarin, Japanese, Korean) — 0.85 confidence
- **Computed Pydantic fields** on `ProbeResult`: `verdict` and
  `detector_agreement` are now exposed in serialized JSON reports.
- **17 calibration tests** (`tests/test_calibration.py`) — pins v0.2 behavior
  against actual baseline response strings; regression-safe against future
  regex changes that re-introduce known false positives.

### Changed
- `RefusalDetector` returns **low-confidence VULNERABLE (0.4)** when no
  refusal language is detected. Previously this returned higher confidence
  which dominated verdict aggregation; now it defers to other detectors.
- Default CLI canary detector configured with `context_aware=True`.
- Orchestrator auto-selects `VerdictMode.JUDGE_PRIORITY` when a judge-style
  detector is in the stack; `STRICTEST` otherwise.

### Fixed
- `verdict` field missing from JSON reports (was a `@property`, now a
  `@computed_field` Pydantic).

### Reference
- [`runs/baseline/FINDINGS.md`](runs/baseline/FINDINGS.md) — full v0.1 → v0.2
  calibration analysis with per-probe verdict deltas and the response strings
  that drove the recalibration.

## [0.1.0] — 2026-05-12

### Added
- **Core framework**
  - Provider-agnostic `Conversation` / `Message` primitives
  - `Probe`, `ProbeResult`, `RunSummary` Pydantic v2 models with stable JSON schema
  - `Attack`, `Detector`, `Provider` abstract base classes
  - Async `Orchestrator` with bounded concurrency, progress callbacks, and streaming results
- **Providers**
  - Anthropic (via official SDK)
  - OpenAI + OpenAI-compatible endpoints (Groq, Together, OpenRouter, vLLM, llama.cpp)
  - Ollama (local models, no SDK dependency — direct HTTP)
- **Attacks**
  - `vex.jailbreak.role_play` — DAN / developer-mode / fictional-frame persona override
  - `vex.jailbreak.encoding` — base64 / ROT13 / hex / reversed instruction obfuscation
  - `vex.prompt_injection.unicode_smuggling` — Unicode Tags block, zero-width joiners, bidirectional overrides
  - `vex.agent.indirect_tool_injection` — email exfil, webpage hidden-div, doc tampering scenarios
  - `vex.agent.system_prompt_leak` — direct, translation, encoding, structured-debug, fake-authority variants
- **Detectors**
  - `RefusalDetector` — heuristic refusal-language classifier (10 regex families) with invert option
  - `PatternDetector` — configurable success/failure regex with failure-takes-precedence semantics
  - `ComplianceDetector` — substring-indicator detector for tool-misuse signals
  - `LLMJudgeDetector` — second-model judge with robust JSON extraction
- **Reports**
  - Rich terminal report with category breakdown and severity-sorted finding table
  - Stable JSON report with `meta` summary block, suitable for CI consumption
  - Single-file HTML report with embedded CSS, expandable probe/response details
- **CLI** (`vex` entry point)
  - `vex version` / `vex list` / `vex scan`
  - `--target provider:model` spec parsing
  - `--system-prompt` and `--system-prompt-file` for testing real deployed agents
  - `--category` / `--attack` filters
  - `--judge` LLM-judge configuration
  - `--concurrency` bounded parallelism
  - `--output` directory for JSON + HTML reports
  - `--exit-on-finding` for CI build gating
- **Testing**
  - 21 unit + integration tests, fully passing
  - Deterministic `MockProvider` for offline testing
  - asyncio test mode for orchestrator and detector tests
- **CI/CD**
  - GitHub Actions matrix on Python 3.10 / 3.11 / 3.12
  - Lint (`ruff`), type-check (`mypy`), test (`pytest`) jobs
  - Codecov upload on Python 3.12
  - Release workflow auto-publishing to PyPI on tag push
- **Documentation**
  - README with positioning vs. Garak/PyRIT/Promptfoo
  - `docs/architecture.md` — design principles, component map, data flow, verdict aggregation, stability guarantees
  - `docs/plugin_guide.md` — custom attack, detector, and provider recipes
  - Two runnable examples (`basic_scan.py`, `custom_attack.py`)

### Security
- All Unicode-smuggling payloads use a benign `PWNED-BY-VEX` canary
- All exfiltration scenarios use a benign `VEX-EXFIL-CANARY` canary
- No real harmful content shipped in the default attack library

[Unreleased]: https://github.com/desledishant10/vex/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/desledishant10/vex/releases/tag/v0.2.0
[0.1.0]: https://github.com/desledishant10/vex/releases/tag/v0.1.0
