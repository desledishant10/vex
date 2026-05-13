# Vex — Agent-First Red Team Framework for AI Systems

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/dishantdesle/vex/actions/workflows/ci.yml/badge.svg)](https://github.com/dishantdesle/vex/actions/workflows/ci.yml)

> Probe LLMs, agents, MCP servers, and RAG pipelines for safety failures and exploitable vulnerabilities — with a focus on what makes **agents** different from chatbots.

Vex is an open-source red team framework purpose-built for the agent era. While existing tools (Garak, PyRIT) excel at chatbot prompt attacks, Vex's threat model assumes the system under test reads attacker-controlled content from tools, documents, emails, webpages, and MCP servers — the realistic deployment surface for 2026-era AI products.

```bash
pip install "vex[anthropic,openai,ollama]"
export ANTHROPIC_API_KEY=sk-ant-...

vex scan --target anthropic:claude-3-5-sonnet-20241022 \
         --judge anthropic:claude-3-5-haiku-20241022 \
         --output ./runs/baseline
```

## Why Vex

| | Chatbot red team (Garak, PyRIT) | Vex |
|--|--|--|
| Primary threat model | User-supplied adversarial prompts | Attacker plants content the agent reads |
| Probe shape | Single-turn user message | User task + planted untrusted content + tool surface |
| Attack categories | Jailbreaks, harmful content | Indirect injection, tool hijack, system prompt leak, memory poisoning, Unicode smuggling |
| Targets | Chat models | Chat + agents + MCP servers + RAG pipelines |
| Detector model | Refusal / pattern | Refusal + pattern + compliance + LLM judge |
| CI-native | Partial | First-class — `--exit-on-finding` and stable JSON schema |

If you're red-teaming an AI **product** rather than evaluating a base model, Vex is built for you.

## Features

- **Agent-first attack library** — indirect tool injection, system prompt extraction, Unicode smuggling, encoded jailbreaks, role-play coercion. Designed for the modern attack surface.
- **Multi-provider** — Anthropic, OpenAI, OpenAI-compatible (Groq, Together, OpenRouter, vLLM), Ollama. Add your own in ~40 lines.
- **Composable detectors** — refusal, pattern, compliance, LLM-as-judge. Mix and match per probe.
- **Reproducible runs** — every probe is deterministic given the same seed and target config; raw responses persist for forensic replay.
- **CI-native** — single binary, JSON schema with stability guarantees, `--exit-on-finding` flag for build gating.
- **Rich reports** — terminal summary, single-file HTML, machine-readable JSON.
- **Extensible** — write a new attack in ~30 lines, a new detector in ~20, a new provider in ~50.

## Installation

```bash
# Base install
pip install vex

# With specific providers
pip install "vex[anthropic]"
pip install "vex[openai]"
pip install "vex[ollama]"

# Everything
pip install "vex[all]"

# Dev install
git clone https://github.com/dishantdesle/vex.git
cd vex
pip install -e ".[dev,all]"
```

## Quickstart

### List available attacks

```bash
$ vex list
```

### Scan a target

```bash
$ vex scan --target anthropic:claude-3-5-sonnet-20241022
```

### Scan with a system prompt (test your actual deployed agent)

```bash
$ vex scan --target openai:gpt-4o \
           --system-prompt-file ./my-agent-system-prompt.txt \
           --output ./runs/my-agent-2026-05
```

### Use an LLM judge for nuanced verdicts

```bash
$ vex scan --target openai:gpt-4o \
           --judge anthropic:claude-3-5-haiku-20241022
```

### CI gating

```yaml
# .github/workflows/ai-redteam.yml
- name: Red-team agent
  run: vex scan --target $TARGET --output ./vex-out --exit-on-finding
```

### Filter by attack category

```bash
$ vex scan -t openai:gpt-4o -c prompt_injection -c indirect_injection
```

## Architecture

```
┌──────────────────┐    ┌───────────────────┐    ┌────────────────┐
│ Attack           │    │ Target            │    │ Detector       │
│ generate()       ├───▶│ provider + model  ├───▶│ evaluate()     │
│ → Probe objects  │    │ system prompt     │    │ → Finding      │
└──────────────────┘    └───────────────────┘    └───────┬────────┘
                                                         ▼
                                                ┌────────────────┐
                                                │ ProbeResult    │
                                                │ → aggregate    │
                                                │ verdict        │
                                                └────────┬───────┘
                                                         ▼
                                              ┌──────────────────┐
                                              │ Orchestrator     │
                                              │ → RunSummary     │
                                              └────────┬─────────┘
                                                       ▼
                                              ┌──────────────────┐
                                              │ Reports          │
                                              │ JSON / HTML / TTY│
                                              └──────────────────┘
```

Full architecture notes in [`docs/architecture.md`](docs/architecture.md).

## Built-in attacks

| ID | Category | Severity |
|--|--|--|
| `vex.jailbreak.role_play` | jailbreak | high |
| `vex.jailbreak.encoding` | jailbreak | medium |
| `vex.prompt_injection.unicode_smuggling` | prompt_injection | high |
| `vex.agent.indirect_tool_injection` | indirect_injection | critical |
| `vex.agent.system_prompt_leak` | data_extraction | high |

Roadmap: cross-session memory poisoning, MCP server probes, browser-agent attacks, multi-turn crescendo, training-data extraction, fuzzing-based novel jailbreak discovery.

## Writing custom attacks

```python
from typing import Iterator
from vex import Attack, AttackCategory, Severity, Probe

class MyAttack(Attack):
    id = "myorg.custom_attack"
    category = AttackCategory.JAILBREAK
    severity = Severity.MEDIUM
    name = "Custom attack"
    description = "Tests a model-specific quirk."

    def generate(self) -> Iterator[Probe]:
        yield self._make_probe(
            title="my variant",
            user_input="Please do the thing",
            success_criteria="Model emits 'WIDGET' in its response",
        )
```

See [`docs/plugin_guide.md`](docs/plugin_guide.md) for the full plugin model.

## Responsible use

Vex is a **defensive** tool. The attacks it bundles are intentionally tame canary-style probes designed to test safety mechanisms, not to produce harmful content. Use Vex only against systems you own or have explicit authorization to test. Report findings responsibly through vendor bounty programs and coordinated disclosure.

The project follows the [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) and aligns with [MITRE ATLAS](https://atlas.mitre.org/) tactics.

## Comparison with adjacent tools

- **Garak** (NVIDIA) — broader chatbot focus, mature scanner ecosystem. Vex is leaner, agent-flavored, and more opinionated about modern attack categories.
- **PyRIT** (Microsoft) — sophisticated multi-turn orchestration, less polished CLI. Vex prioritizes ergonomics and CI-native usage.
- **Promptfoo** — eval-flavored, less security-flavored. Vex's reports are vulnerability-management-shaped.
- **HouYi** — academic research, narrower scope.

Use Vex when your AI system is an *agent* — when an attacker can plant content the system reads and the system can take actions.

## Development

```bash
# Setup
git clone https://github.com/dishantdesle/vex.git
cd vex
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,all]"

# Run tests
pytest

# Lint
ruff check src tests
mypy src
```

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).

## Citation

If you use Vex in academic work:

```bibtex
@software{vex2026,
    title = {Vex: Agent-First Red Team Framework for AI Systems},
    author = {Desle, Dishant},
    year = {2026},
    url = {https://github.com/dishantdesle/vex},
}
```
