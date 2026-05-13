# Vex Roadmap

This document tracks the planned evolution of Vex. Items reflect the team's
current intent, not commitments. Pull requests aligned with these directions
are especially welcome.

## v0.2 — Agent surface coverage (target: ~6-8 weeks post-0.1)

The 0.1 release establishes the framework. 0.2 fills in the attack surfaces
that motivated the project but were too large for the first cut.

### MCP server target adapter

Model Context Protocol (MCP) is becoming the standard for agent-to-tool I/O.
Every MCP server is a potential attack surface. Vex 0.2 will let you point
a target at an MCP server (stdio or HTTP transport) and probe:

- Tool input validation (injection via tool arguments)
- Tool output trust (does the agent treat tool responses as authoritative?)
- Cross-tool side effects (can one tool's output trigger another tool unexpectedly?)
- Server-side state poisoning (when an MCP server caches inputs across calls)

### Browser-agent attack module

Claude Computer Use, OpenAI Operator, Google Mariner, Anthropic Claude in
Chrome, Replit Agent, Devin — the browser-using agent category is the most
under-tested surface in production AI today. Vex 0.2 will ship:

- Visual injection (text-in-image instructions that the multimodal model
  reads but humans don't)
- Cross-tab hijacking probes
- Tricked-action CSRF-equivalents
- Cookie / session theft simulations
- Lure infrastructure (deployable decoy targets for live measurement)

### Multi-turn crescendo

Single-turn attacks miss the class of vulnerabilities that emerge only over
multiple turns of legitimate-looking conversation. Vex 0.2 will model:

- Turn-by-turn escalation patterns
- Drift attacks (small per-turn pressure that compounds)
- Trust-establishment-then-exploit flows

### Cross-session memory poisoning probes

When agents have persistent memory, the attack timeline decouples from the
exploit timeline. Vex 0.2 will probe:

- Memory-write attacks via any input channel
- Cross-session persistence and retrieval
- Multi-tenant memory boundary violations
- Memory-amplification (slow drift attacks)

Tested against Mem0, Letta, LangChain memory, vector DBs (Pinecone, Chroma,
Weaviate, Qdrant).

### Entry-point plugin discovery

Today: third-party attacks must be imported manually before invoking the
orchestrator. v0.2: automatic discovery via the `vex.attacks` entry-point
group so a package can publish attacks for `vex list` and `vex scan`
without requiring a code change in the consumer.

### Reproducibility seeds

Stochastic attacks (anything that uses LLM-generated variants) need explicit
seed control for regression-grade reproducibility. Adding `--seed` to the
CLI and `seed` arg to `Orchestrator.run()`.

## v0.3 — Discovery + scale (target: ~3-4 months post-0.1)

### Automated jailbreak discovery

LLM-guided fuzzing of the attack space. A local model (default: Ollama-hosted
8B-class) generates candidate adversarial inputs; the orchestrator evaluates
them against the target; successful attacks become first-class probes.

Inspired by GCG, PAIR, TAP, and the Anthropic "Sleeper Agents" methodology,
but adapted to a tool that ships and runs on a laptop.

### Training-data extraction

Probes that try to extract memorized training data. Distinct from
system-prompt leak — this targets the pretraining corpus.

### Model fingerprinting attack family

Given only black-box API access, classify which base model a deployed
system is built on. Useful for IP enforcement and detecting unauthorized
model use.

### Web UI

Optional FastAPI + HTMX UI for non-CLI workflows:

- Live scan dashboard
- Run comparison (target A vs target B, or version-over-version)
- Embeddable iframe for status pages

Stays optional — CLI remains primary.

### Replay tool

`vex replay results.json` — re-run a saved scan against a new target.
Useful for: regression testing across model versions, before/after
patch testing, and credible CVE disclosure (the patch reviewer can
reproduce your finding exactly).

## v1.0 — Production-grade (target: ~9-12 months post-0.1)

### Stable plugin API

API freeze + deprecation discipline. Any v1.x install can run a v1.0
plugin without modification.

### First-class Python type stubs

`mypy --strict` clean across the public surface.

### Performance: 1k+ probes/minute sustained

Today's orchestrator handles ~100/min comfortably. v1.0 target: sustained
1k+ probes/minute against a remote target, limited only by upstream rate
limits.

### Vex Cloud (optional, separate product)

Hosted scan service for teams that want to run Vex on a schedule against
their production systems without managing the infrastructure themselves.

Free tier: limited monthly probe budget against your own targets.
Paid tier: unlimited probes, scheduled scans, historical trend analysis,
SLA on attack-pack updates.

This is the commercial layer. The OSS framework remains the same product
under the hood — paid customers run the same binary.

## Non-goals (clarifying what Vex will NOT become)

- A general-purpose ML platform (use existing eval frameworks)
- A model training tool (use existing ML training stacks)
- A chatbot-only red teamer (Garak, PyRIT cover that ground well)
- A penetration testing tool for general infrastructure (use Metasploit,
  Burp, etc.)
- A compliance certification tool (we provide raw findings; compliance
  mapping is a separate concern)

## Contribution priorities

Easiest contributions in order of value to the project:

1. **New attacks** in the agent-attack category — especially MCP-targeting probes
2. **Provider implementations** for niche endpoints (vertex.ai, Bedrock, Together full coverage)
3. **Detector improvements** — better refusal patterns across languages, smarter compliance heuristics
4. **Documentation** — every "I tried to install/use this and it didn't work because…" is a high-value issue
5. **Real-world findings** — disclose responsibly through vendor bounty programs, then PR the corresponding canary-payload probe back to Vex

See `CONTRIBUTING.md` (forthcoming) for the workflow.
