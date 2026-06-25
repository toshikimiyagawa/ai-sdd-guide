from pathlib import Path

ROOT = Path(__file__).parents[1]


def read(path):
    return (ROOT / path).read_text()


# --- core.md ---

def test_core_untracked_ac_stop():
    content = read("rules/core.md")
    assert "every Issue AC must appear in" in content
    assert "STOP — do not freeze and do not implement" in content


def test_core_frozen_artifact_immutable():
    content = read("rules/core.md")
    assert "Frozen artifacts" in content
    assert "only permitted post-freeze edit" in content
    assert "[ ] → [x]" in content


# --- issue-intake.md ---

def test_intake_freeze_gate_section():
    content = read("rules/issue-intake.md")
    assert "## Tier 2 freeze gate" in content
    assert "<issue番号>-AC<連番>" in content
    assert "traceability.json" in content
    assert "freeze is blocked" in content


def test_intake_out_of_scope_followup_required():
    content = read("rules/issue-intake.md")
    assert "followup_issue" in content
    assert "No orphaned scope-outs allowed" in content


def test_intake_weakened_spec_approval():
    content = read("rules/issue-intake.md")
    assert "weaker than the Issue" in content
    assert "explicit human approval" in content


def test_intake_never_freeze_untracked():
    content = read("rules/issue-intake.md")
    assert "Never freeze a Tier 2 spec that has untracked Issue ACs" in content
