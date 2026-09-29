"""Negative fixture tests: validator must ERROR on invalid fixtures, PASS on valid ones."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
VALIDATOR = ROOT / "integration" / "ci" / "sdd-validate.sh"


def _run_validator(fixture_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(VALIDATOR), "--root", str(fixture_path)],
        capture_output=True,
        text=True,
    )


def _prepare_valid_fixture(fixture_name: str, tmp_path: Path) -> Path:
    """Copy valid fixture to tmp_path, inject real git HEAD SHA into evidence.json."""
    src = FIXTURES / fixture_name
    dest = tmp_path / fixture_name
    shutil.copytree(src, dest)
    evidence_path = dest / "specs" / "my-feature" / "evidence.json"
    if evidence_path.exists():
        try:
            sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True,
                cwd=str(ROOT),
            ).stdout.strip()
        except subprocess.CalledProcessError:
            pytest.skip("git rev-parse HEAD failed — skipping valid evidence fixture")
        evidence = json.loads(evidence_path.read_text())
        evidence["commit_sha"] = sha
        evidence_path.write_text(json.dumps(evidence, indent=2))
    return dest


# ---------------------------------------------------------------------------
# Negative fixtures — validator must exit 1 with expected error fragment
# ---------------------------------------------------------------------------

NEGATIVE_CASES = [
    ("fixture-incomplete-tasks",    "unchecked item"),
    ("fixture-wrong-state",         "no matching entry"),
    ("fixture-missing-tasks-entry", "no entry for feature"),
    ("fixture-phase-mismatch",      "does not match tasks.json entry"),
    ("fixture-no-test-mapping",     "test file not found"),
    ("fixture-orphan-spec-ac",      "not found in spec.md"),
    ("fixture-duplicate-spec-ac",         "duplicate spec_ac"),
    ("fixture-scope-out-no-followup",     "missing HTTP(S) followup_issue"),
    ("fixture-weakened-ac",               "snapshot AC not tracked in traceability"),
    ("fixture-stale-snapshot-hash",       "body_hash does not match"),
    ("fixture-untracked-issue-ac",        "traceability AC not in snapshot"),
    ("fixture-invalid-evidence-commit",   "commit_sha not found in git repository"),
    ("fixture-non-test-count",            "is not of type 'null'"),
    ("fixture-missing-test-count",        "is not of type 'integer'"),
]


@pytest.mark.parametrize("fixture_name,expected_fragment", NEGATIVE_CASES)
def test_negative_fixture_fails(fixture_name, expected_fragment):
    result = _run_validator(FIXTURES / fixture_name)
    assert result.returncode == 1, (
        f"{fixture_name}: expected exit 1, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert expected_fragment in result.stderr, (
        f"{fixture_name}: expected '{expected_fragment}' in stderr\n"
        f"stderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Valid fixtures — validator must exit 0
# ---------------------------------------------------------------------------

VALID_CASES = [
    "fixture-incomplete-tasks-valid",
    "fixture-wrong-state-valid",
    "fixture-missing-tasks-entry-valid",
    "fixture-phase-mismatch-valid",
    "fixture-no-test-mapping-valid",
    "fixture-orphan-spec-ac-valid",
    "fixture-duplicate-spec-ac-valid",
    "fixture-scope-out-no-followup-valid",
    "fixture-weakened-ac-valid",
    "fixture-stale-snapshot-hash-valid",
    "fixture-untracked-issue-ac-valid",
    "fixture-invalid-evidence-commit-valid",
    "fixture-non-test-count-valid",
    "fixture-missing-test-count-valid",
]


@pytest.mark.parametrize("fixture_name", VALID_CASES)
def test_valid_fixture_passes(fixture_name, tmp_path):
    fixture_path = _prepare_valid_fixture(fixture_name, tmp_path)
    result = _run_validator(fixture_path)
    assert result.returncode == 0, (
        f"{fixture_name}: expected exit 0, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
