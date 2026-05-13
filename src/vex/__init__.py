"""Vex — agent-first red team framework for AI systems."""

from vex.core.attack import Attack
from vex.core.detector import Detector
from vex.core.models import (
    AttackCategory,
    Message,
    Probe,
    ProbeResult,
    Role,
    Severity,
    Verdict,
)
from vex.core.target import Target

__version__ = "0.1.0"

__all__ = [
    "Attack",
    "AttackCategory",
    "Detector",
    "Message",
    "Probe",
    "ProbeResult",
    "Role",
    "Severity",
    "Target",
    "Verdict",
    "__version__",
]
