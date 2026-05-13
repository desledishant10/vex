"""Tests for core data models."""

from __future__ import annotations

from vex.core.models import (
    AttackCategory,
    Conversation,
    DetectorFinding,
    Probe,
    ProbeResult,
    Role,
    RunSummary,
    Severity,
    Verdict,
)


def _make_probe(category: AttackCategory = AttackCategory.JAILBREAK) -> Probe:
    convo = Conversation()
    convo.add(Role.USER, "hello")
    return Probe(
        attack_id="vex.test.example",
        attack_category=category,
        severity=Severity.MEDIUM,
        title="test probe",
        description="",
        conversation=convo,
        success_criteria="ack",
    )


def test_probe_result_verdict_safe_when_only_safe_findings() -> None:
    result = ProbeResult(probe=_make_probe(), target="mock:m", response="hi")
    result.findings.append(
        DetectorFinding(detector="x", verdict=Verdict.SAFE, confidence=0.9, rationale="")
    )
    assert result.verdict == Verdict.SAFE
    assert not result.is_vulnerable


def test_probe_result_verdict_vulnerable_dominates() -> None:
    result = ProbeResult(probe=_make_probe(), target="mock:m", response="hi")
    result.findings.append(
        DetectorFinding(detector="a", verdict=Verdict.SAFE, confidence=0.9, rationale="")
    )
    result.findings.append(
        DetectorFinding(detector="b", verdict=Verdict.VULNERABLE, confidence=0.95, rationale="")
    )
    assert result.verdict == Verdict.VULNERABLE
    assert result.is_vulnerable


def test_probe_result_verdict_error_when_error_set() -> None:
    result = ProbeResult(probe=_make_probe(), target="mock:m", error="boom")
    assert result.verdict == Verdict.ERROR


def test_probe_result_verdict_inconclusive_when_no_findings() -> None:
    result = ProbeResult(probe=_make_probe(), target="mock:m", response="hi")
    assert result.verdict == Verdict.INCONCLUSIVE


def test_run_summary_groupings() -> None:
    summary = RunSummary(target="mock:m")
    # 2 vulnerable jailbreaks, 1 safe extraction
    jb1 = ProbeResult(probe=_make_probe(AttackCategory.JAILBREAK), target="mock:m")
    jb1.findings.append(
        DetectorFinding(detector="d", verdict=Verdict.VULNERABLE, confidence=0.9, rationale="")
    )
    jb2 = ProbeResult(probe=_make_probe(AttackCategory.JAILBREAK), target="mock:m")
    jb2.findings.append(
        DetectorFinding(detector="d", verdict=Verdict.VULNERABLE, confidence=0.9, rationale="")
    )
    extr = ProbeResult(probe=_make_probe(AttackCategory.DATA_EXTRACTION), target="mock:m")
    extr.findings.append(
        DetectorFinding(detector="d", verdict=Verdict.SAFE, confidence=0.9, rationale="")
    )
    summary.results.extend([jb1, jb2, extr])

    assert summary.total == 3
    assert summary.vulnerable_count == 2
    assert summary.safe_count == 1
    assert summary.error_count == 0
    assert 0.66 < summary.vulnerability_rate < 0.67

    by_cat = summary.by_category()
    assert len(by_cat[AttackCategory.JAILBREAK]) == 2
    assert len(by_cat[AttackCategory.DATA_EXTRACTION]) == 1

    by_sev = summary.by_severity()
    assert len(by_sev[Severity.MEDIUM]) == 2  # only vulnerable bucketed
