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
    ("fixture-incomplete-tasks", "unchecked item"),
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
]


@pytest.mark.parametrize("fixture_name", VALID_CASES)
def test_valid_fixture_passes(fixture_name, tmp_path):
    fixture_path = _prepare_valid_fixture(fixture_name, tmp_path)
    result = _run_validator(fixture_path)
    assert result.returncode == 0, (
        f"{fixture_name}: expected exit 0, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
