"""sdd-check.yml must work when copied into a consumer with the guide at vendor/ai-sdd-guide."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / "integration" / "ci" / "sdd-check.yml"


def _step_run_script(text: str, step_name: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"- name: {step_name}")
    run_idx = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "run: |")
    body_indent = len(lines[run_idx]) - len(lines[run_idx].lstrip()) + 2
    body = []
    for line in lines[run_idx + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) < body_indent:
            break
        body.append(line[body_indent:])
    return "\n".join(body) + "\n"


def _run_validate_step(tmp_path, head_ref, labels=""):
    (tmp_path / "vendor").mkdir(exist_ok=True)
    link = tmp_path / "vendor" / "ai-sdd-guide"
    if not link.exists():
        link.symlink_to(ROOT)
    script = _step_run_script(WORKFLOW.read_text(), "Run sdd-validate")
    env = {**os.environ, "SDD_HEAD_REF": head_ref, "SDD_PR_LABELS": labels}
    return subprocess.run(
        ["bash", "-e", "-c", script], cwd=tmp_path, capture_output=True, text=True, env=env
    )


def test_sdd_validate_step_runs_in_consumer_layout(tmp_path):
    result = _run_validate_step(tmp_path, "t0/1-x")
    assert result.returncode == 0, result.stdout + result.stderr


def test_sdd_validate_step_rejects_bad_branch(tmp_path):
    result = _run_validate_step(tmp_path, "feat/x")
    assert result.returncode == 1, result.stdout + result.stderr


def test_sdd_validate_step_rejects_tier2_without_specs(tmp_path):
    result = _run_validate_step(tmp_path, "t2/1-x")
    assert result.returncode == 1, result.stdout + result.stderr


def test_sdd_validate_step_rejects_label_mismatch(tmp_path):
    result = _run_validate_step(tmp_path, "t0/1-x", "sdd:tier-2")
    assert result.returncode == 1, result.stdout + result.stderr
