import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
HOOK = ROOT / "integration" / "hooks" / "codex-sdd-guard.sh"
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test User",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test User",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


def _run(command, cwd):
    subprocess.run(command, cwd=cwd, check=True, text=True, env=GIT_ENV)


def _make_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(["git", "init"], repo)
    _run(["git", "config", "user.email", "test@example.invalid"], repo)
    _run(["git", "config", "user.name", "Test User"], repo)

    (repo / ".sdd").mkdir()
    (repo / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 1, "phase": "implement"}) + "\n"
    )
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('hello')\n")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "init"], repo)

    worktree = repo / ".worktrees" / "feature"
    _run(["git", "worktree", "add", str(worktree), "-b", "feature"], repo)
    return repo, worktree


def _guard(cwd, payload):
    return subprocess.run(
        ["bash", str(HOOK)],
        cwd=cwd,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
        env=GIT_ENV,
    )


def _deny_reason(result):
    if not result.stdout.strip():
        return ""
    return json.loads(result.stdout)["hookSpecificOutput"].get(
        "permissionDecisionReason", ""
    )


def test_apply_patch_absolute_path_in_linked_worktree_is_allowed_from_primary_cwd(tmp_path):
    repo, worktree = _make_repo(tmp_path)
    patch = f"""*** Begin Patch
*** Update File: {worktree / 'src' / 'app.py'}
@@
-print('hello')
+print('hello from worktree')
*** End Patch
"""

    result = _guard(repo, {"tool_name": "apply_patch", "tool_input": {"patch": patch}})

    assert result.stdout == ""


def test_apply_patch_relative_path_uses_tool_workdir_for_worktree_detection(tmp_path):
    repo, worktree = _make_repo(tmp_path)
    patch = """*** Begin Patch
*** Update File: src/app.py
@@
-print('hello')
+print('hello from worktree')
*** End Patch
"""

    result = _guard(
        repo,
        {
            "tool_name": "apply_patch",
            "tool_input": {"patch": patch, "workdir": str(worktree)},
        },
    )

    assert result.stdout == ""


def test_apply_patch_primary_checkout_source_edit_is_denied(tmp_path):
    repo, _ = _make_repo(tmp_path)
    patch = f"""*** Begin Patch
*** Update File: {repo / 'src' / 'app.py'}
@@
-print('hello')
+print('hello from primary')
*** End Patch
"""

    result = _guard(repo, {"tool_name": "apply_patch", "tool_input": {"patch": patch}})

    assert "source edits are only allowed from a linked git worktree" in _deny_reason(result)


def test_bash_read_with_stderr_redirect_is_not_treated_as_write(tmp_path):
    repo, _ = _make_repo(tmp_path)

    result = _guard(
        repo,
        {
            "tool_name": "Bash",
            "tool_input": {
                "command": f"sed -n '1,120p' {repo / 'src' / 'app.py'} 2>/dev/null || true"
            },
        },
    )

    assert result.stdout == ""


def test_bash_explicit_fd_redirect_write_is_detected(tmp_path):
    repo, _ = _make_repo(tmp_path)

    result = _guard(
        repo,
        {
            "tool_name": "Bash",
            "tool_input": {"command": f"echo x 1> {repo / 'src' / 'app.py'}"},
        },
    )

    assert "source edits are only allowed from a linked git worktree" in _deny_reason(result)


def test_bash_plain_redirect_write_is_detected(tmp_path):
    repo, _ = _make_repo(tmp_path)

    result = _guard(
        repo,
        {
            "tool_name": "Bash",
            "tool_input": {"command": f"echo x > {repo / 'src' / 'app.py'}"},
        },
    )

    assert "source edits are only allowed from a linked git worktree" in _deny_reason(result)


def test_bash_stderr_redirect_to_real_file_is_detected(tmp_path):
    repo, _ = _make_repo(tmp_path)

    result = _guard(
        repo,
        {
            "tool_name": "Bash",
            "tool_input": {"command": f"echo log 2> {repo / 'src' / 'out.py'}"},
        },
    )

    assert "source edits are only allowed from a linked git worktree" in _deny_reason(result)


def test_bash_fd_dup_redirect_is_not_treated_as_write(tmp_path):
    repo, _ = _make_repo(tmp_path)

    result = _guard(
        repo,
        {
            "tool_name": "Bash",
            "tool_input": {"command": f"cat {repo / 'src' / 'app.py'} 2>&1"},
        },
    )

    assert result.stdout == ""
