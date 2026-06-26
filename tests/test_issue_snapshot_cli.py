"""Tests for sdd-issue-snapshot CLI."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
CLI_SCRIPT = ROOT / "integration" / "ci" / "sdd-issue-snapshot.py"


def test_cli_writes_snapshot_from_body_file(tmp_path):
    body = "## 受入条件\n\n- [ ] first criterion\n- [x] second criterion\n"
    body_file = tmp_path / "issue.md"
    output_file = tmp_path / "issue-snapshot.json"
    body_file.write_text(body)

    result = subprocess.run(
        [
            "python3",
            str(CLI_SCRIPT),
            "--issue",
            "53",
            "--feature",
            "issue-snapshot",
            "--body-file",
            str(body_file),
            "--url",
            "https://github.com/owner/repo/issues/53",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(output_file.read_text())
    assert data["issue"] == 53
    assert data["url"] == "https://github.com/owner/repo/issues/53"
    assert data["raw_body"] == body
    assert data["body_hash"] == hashlib.sha256(body.encode("utf-8")).hexdigest()
    assert data["stable_acs"] == [
        {"id": "53-AC1", "text": "first criterion"},
        {"id": "53-AC2", "text": "second criterion"},
    ]
