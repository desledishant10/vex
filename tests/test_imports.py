"""Import-surface smoke tests.

The provider, CLI, and report modules were historically outside CI's import
graph: nothing in the suite imported them, and ``reports/`` was even gitignored,
so a syntax or import error in any of them passed CI green (which is how a
missing ``reports`` package shipped in a wheel that crashed on import). These
tests import every user-facing module across the whole Python matrix so that
regression cannot recur.

Providers guard their SDK imports inside ``__init__``, so importing the modules
needs no provider extras - only the base install plus ``[dev]``.
"""

from __future__ import annotations

import importlib

import pytest

PROVIDER_MODULES = [
    "vex.providers.anthropic",
    "vex.providers.openai",
    "vex.providers.ollama",
]

USER_FACING_MODULES = [
    "vex.cli",
    "vex.reports",
    "vex.reports.html",
    "vex.reports.json_report",
    "vex.reports.terminal",
]


@pytest.mark.parametrize("module", PROVIDER_MODULES + USER_FACING_MODULES)
def test_module_imports(module: str) -> None:
    importlib.import_module(module)


def test_provider_classes_exposed() -> None:
    from vex.providers.anthropic import AnthropicProvider
    from vex.providers.ollama import OllamaProvider
    from vex.providers.openai import OpenAIProvider

    assert AnthropicProvider.name == "anthropic"
    assert OpenAIProvider.name == "openai"
    assert OllamaProvider.name == "ollama"


def test_ollama_provider_instantiates_without_extras() -> None:
    # Ollama talks HTTP via httpx (a core dependency), so it must construct with
    # no provider extra installed - unlike the SDK-backed providers.
    from vex.providers.ollama import OllamaProvider

    provider = OllamaProvider(base_url="http://localhost:11434")
    assert provider.name == "ollama"
