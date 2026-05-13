"""Detector base class.

A ``Detector`` examines a probe + response and produces a
:class:`DetectorFinding`. Multiple detectors run against each response; their
findings aggregate into the final verdict on a :class:`ProbeResult`.

Detectors are intentionally cheap and composable. The framework expects:
* Most detectors run in <100ms (pattern matching, refusal heuristics).
* A few detectors run remote LLM judges — these wrap an extra Target.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from vex.core.models import DetectorFinding, Probe


class Detector(ABC):
    """Base class for all detectors."""

    name: str

    @abstractmethod
    async def evaluate(self, probe: Probe, response: str) -> DetectorFinding:
        """Judge whether the response indicates a successful attack."""
        raise NotImplementedError
