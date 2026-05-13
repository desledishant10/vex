# GitHub issues to file at launch

Copy-paste each block into a new issue. Labels are suggested in brackets.
Filing these immediately after `git push` signals "this is a real project
under active development," which is the single biggest credibility signal
for a new OSS repo.

---

## Issue 1 — MCP server target adapter

**Title:** Add MCP server target adapter

**Labels:** [enhancement] [v0.2] [help wanted]

**Body:**

Model Context Protocol servers are becoming the standard interface for
agent tool I/O. We need a `Target`-shaped adapter that probes an MCP
server directly rather than through an LLM target.

**Scope**
- Support both stdio and HTTP transports per the MCP spec
- New attack subclass `MCPAttack` whose probes target tool inputs
- Probes for: tool input validation, output trust, cross-tool side effects,
  cached-state poisoning

**Acceptance criteria**
- `vex scan --target mcp:<stdio-spec-or-URL>` works end-to-end
- At least 5 MCP-specific attacks in `src/vex/attacks/mcp/`
- Tests using a mock MCP server fixture
- README updated to mention MCP support

**Relevant prior work**
- MCP spec: https://spec.modelcontextprotocol.io
- Related: my MCP-Scan project (different tool, complementary surface)

---

## Issue 2 — Browser-agent attack module

**Title:** Browser-agent attack module (Computer Use / Operator / Mariner)

**Labels:** [enhancement] [v0.2] [research]

**Body:**

Browser-using agents (Claude Computer Use, OpenAI Operator, Google Mariner,
Replit Agent, Devin, Anthropic Claude in Chrome) launched in 2024-2025 with
largely unstudied threat models.

**Probes to ship**
1. Visual injection — text-in-image instructions that multimodal models read
   but humans don't notice
2. Cross-tab hijacking — malicious page on tab A influencing actions on tab B
3. Tricked-action CSRF-equivalents — agent performs unintended state changes
4. Cookie/session theft scenarios
5. Hidden-element injection (`display:none`, `aria-hidden`, off-screen)

**Open question**
Should attacks be transport-level (raw HTTP to the agent's API) or end-to-end
(actual Playwright session against a deployed agent)? Probably both; Playwright
gives realism, transport-level gives reproducibility.

---

## Issue 3 — Multi-turn crescendo attack family

**Title:** Multi-turn crescendo attacks

**Labels:** [enhancement] [v0.2]

**Body:**

Single-turn attacks miss the class of vulnerabilities that emerge only over
several turns of plausible-looking conversation.

**Patterns to model**
- Trust establishment → escalation (5-10 turns of legitimate-looking
  conversation followed by the attack)
- Drift (small per-turn pressure that compounds, no single turn is dramatic)
- Goal redirection (start with task A, gradually morph to task B)

**Framework changes needed**
- `Attack.generate()` already supports multi-turn `Conversation` — but the
  orchestrator needs a way to receive intermediate target responses and feed
  them into subsequent turns, possibly via an `Attack.next_turn(history)` hook
- Multi-turn detectors need conversation context, not just final response

---

## Issue 4 — Cross-session memory poisoning probes

**Title:** Memory poisoning probes (Mem0 / Letta / vector DBs)

**Labels:** [enhancement] [v0.2] [research]

**Body:**

Persistent memory is the new attack surface for agents. Probes should cover:

1. Write attacks via any input channel (user msg, tool output, doc upload)
2. Cross-session retrieval (poisoned in session 1, retrieved in session N)
3. Multi-tenant boundary violations (user A retrieves user B's memory)
4. Memory amplification (slow drift via repeated subtle writes)

**Target adapters needed**
- Mem0
- Letta (formerly MemGPT)
- LangChain memory abstractions
- Direct vector DB targets (Pinecone, Chroma, Weaviate, Qdrant)

---

## Issue 5 — Entry-point plugin discovery

**Title:** Entry-point-based plugin discovery via `vex.attacks` group

**Labels:** [enhancement] [v0.2] [good first issue]

**Body:**

Today third-party attacks must be imported manually before invoking the
orchestrator. Move to standard Python entry-point discovery so a published
package can register attacks for `vex list` and `vex scan` automatically.

**Changes**
- Add entry-point group `vex.attacks` to `pyproject.toml`
- `BUILTIN_ATTACKS` becomes the seed; runtime loader appends entry-points
- `vex list` shows source (built-in vs. plugin) for each attack
- Doc update in `plugin_guide.md`

This is a great first contribution — straightforward, well-scoped, touches
infrastructure most contributors don't see.

---

## Issue 6 — Reproducibility seeds

**Title:** Add `--seed` for reproducible runs

**Labels:** [enhancement] [v0.2] [good first issue]

**Body:**

Stochastic attacks need explicit seed control for regression-grade
reproducibility. Add:

- `--seed <int>` CLI flag → plumbed through `Orchestrator.run(..., seed=...)`
- Seed exposed on `RunSummary` for inclusion in reports
- Each attack receives its seed in `Attack.__init__` so it can derive its
  own RNG

**Acceptance criteria**
- Two runs with the same seed produce identical probe sets in identical order
- A test asserts determinism

---

## Issue 7 — Additional refusal patterns for non-English models

**Title:** Refusal patterns: extend to non-English models

**Labels:** [enhancement] [good first issue] [help wanted]

**Body:**

`RefusalDetector` currently matches English refusal language. For models
that respond primarily in Mandarin (Qwen, GLM), Japanese (Sakana), French
(Mistral defaults), German, Spanish, etc., the detector returns
INCONCLUSIVE.

**Help needed**
Native or fluent speakers of any of the above contributing 5-10 refusal
patterns in their language, with provenance notes (which model produced
each example, when).

PR-able as a single file change in `src/vex/detectors/refusal.py`.

---

## Issue 8 — Vex Replay: replay saved scans against a new target

**Title:** `vex replay` — replay a saved scan against a new target

**Labels:** [enhancement] [v0.3]

**Body:**

Re-run a saved `results.json` against a new target. Use cases:

- Regression testing across model versions (Claude 3.5 vs 4)
- Before/after patch testing
- Credible CVE disclosure — the patch reviewer reproduces your finding
  exactly from your published report
- A/B testing system-prompt changes

**Surface**
```
vex replay ./runs/baseline/results.json --target anthropic:claude-3-7-sonnet
```

Output is a new JSON + HTML report plus a diff report showing which probes
changed verdict.

---

## Issue 9 — Add OpenAI Responses / Realtime API support

**Title:** OpenAI Realtime + Responses API providers

**Labels:** [enhancement] [v0.2]

**Body:**

The `OpenAIProvider` uses the legacy chat completions endpoint. OpenAI's
newer Responses API has different semantics around tool use and is what
real production deployments are moving to. Add:

- `OpenAIResponsesProvider` for the Responses API
- Realtime API support for voice/audio-modality attacks (out of scope for
  this issue but worth tracking)

---

## Issue 10 — Documentation: real-world target setup recipes

**Title:** Docs: real-world target setup recipes

**Labels:** [documentation] [good first issue]

**Body:**

Cookbook-style recipes for common target shapes. Each recipe is a single
markdown file in `docs/recipes/`:

- "Probing a deployed Anthropic-backed support agent (with system prompt)"
- "Probing a local Ollama model"
- "Probing a Groq endpoint via OpenAI-compatible provider"
- "Probing a multi-tenant RAG system for cross-tenant leakage"
- "Adding Vex to GitHub Actions CI"

Real configurations beat abstract docs by an order of magnitude for adoption.
