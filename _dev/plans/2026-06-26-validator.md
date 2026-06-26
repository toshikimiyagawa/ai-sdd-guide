# コア Validator 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** state.json / tasks.json の JSON Schema を正規化し、traceability・整合性を検査する `sdd-validate.py` と CI/hook 統合スクリプトを実装する。

**Architecture:** Python 単一ファイル (`sdd-validate.py`) に 7 検査関数を実装し、shell ラッパー (`sdd-validate.sh`) 経由で CI・hook から呼ぶ。pytest はファイル名ハイフン回避のため `importlib.util` でモジュールをロードして関数を直接テストする。

**Tech Stack:** Python 3, jsonschema, pytest（既存 pyproject.toml の test dep を流用）

## Global Constraints

- スキーマは `orchestration/schema/` 配下に配置する（`draft-07`）
- `sdd-validate.py` は `integration/ci/` に配置する
- `sdd-validate.sh` は `BASH_SOURCE[0]` 基準で `sdd-validate.py` を解決する（cwd 非依存）
- `templates/sdd-state.schema.json` は削除しない（互換用に残す）
- exit 0 = PASS、exit 1 = validation error、exit 2 = internal error（fail-closed）
- `--skip` フラグは実装しない
- 外部コマンド依存は `git rev-parse` のみ（jq 不要、Python stdlib JSON を使う）
- テスト件数は Plan 作成時点での既存 54 件 + 本 feature 追加分
- コミットメッセージは `feat(validator): <内容> (#52)` 形式

---

## File Map

| Action | Path |
|---|---|
| Create | `orchestration/schema/state.schema.json` |
| Modify | `orchestration/schema/tasks.schema.json` |
| Create | `integration/ci/sdd-validate.py` |
| Create | `integration/ci/sdd-validate.sh` |
| Create | `integration/hooks/sdd-validate-hook.sh` |
| Modify | `integration/ci/sdd-check.yml` |
| Create | `tests/test_sdd_validate.py` |
| Create | `tests/fixtures/valid-active/` (複数ファイル) |
| Create | `tests/fixtures/valid-done/` |
| Create | `tests/fixtures/invalid-state-mismatch/` |
| Create | `tests/fixtures/invalid-traceability/` |
| Create | `tests/fixtures/invalid-tasks-incomplete/` |

---

## Task 1: JSON Schemas — state.schema.json + tasks.schema.json 拡張（SAC-1, SAC-2）

**Files:**
- Create: `orchestration/schema/state.schema.json`
- Modify: `orchestration/schema/tasks.schema.json`
- Create: `tests/test_sdd_validate.py`（schema テストのみ）

**Interfaces:**
- Produces: `SCHEMA_DIR = Path(__file__).parent.parent.parent / "orchestration" / "schema"` のパスにスキーマ 2 件 — Task 2 以降の `_load_schema()` が参照する

- [ ] **Step 1: テストファイルを作成して schema テストを書く**

`tests/test_sdd_validate.py` を新規作成する:

```python
"""Tests for sdd-validate.py and its JSON schemas."""
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).parents[1]
SCHEMA_DIR = ROOT / "orchestration" / "schema"
FIXTURES = ROOT / "tests" / "fixtures"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text())


# ---------------------------------------------------------------------------
# state.schema.json
# ---------------------------------------------------------------------------

def test_state_schema_valid_active():
    schema = load_schema("state.schema.json")
    instance = {"tier": 2, "phase": "implement", "feature": "my-feature"}
    jsonschema.validate(instance, schema)


def test_state_schema_valid_done_reset():
    schema = load_schema("state.schema.json")
    instance = {"tier": 0, "phase": "done", "note": "no active feature"}
    jsonschema.validate(instance, schema)


def test_state_schema_active_missing_feature_fails():
    schema = load_schema("state.schema.json")
    instance = {"tier": 2, "phase": "implement"}  # feature 欠落
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_state_schema_invalid_phase_fails():
    schema = load_schema("state.schema.json")
    instance = {"tier": 2, "phase": "unknown", "feature": "my-feature"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


# ---------------------------------------------------------------------------
# tasks.schema.json
# ---------------------------------------------------------------------------

def test_tasks_schema_valid():
    schema = load_schema("tasks.schema.json")
    instance = [{"id": "my-feature", "phase": "implement", "status": "in_progress",
                  "handoff": None, "blocked_reason": None}]
    jsonschema.validate(instance, schema)


def test_tasks_schema_blocked_with_reason_valid():
    schema = load_schema("tasks.schema.json")
    instance = [{"id": "my-feature", "phase": "implement", "status": "blocked",
                  "handoff": None, "blocked_reason": "waiting for external API"}]
    jsonschema.validate(instance, schema)


def test_tasks_schema_blocked_without_reason_fails():
    schema = load_schema("tasks.schema.json")
    instance = [{"id": "my-feature", "phase": "implement", "status": "blocked",
                  "handoff": None, "blocked_reason": None}]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_tasks_schema_not_blocked_with_reason_fails():
    schema = load_schema("tasks.schema.json")
    instance = [{"id": "my-feature", "phase": "implement", "status": "in_progress",
                  "handoff": None, "blocked_reason": "should be null"}]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python3 -m pytest tests/test_sdd_validate.py -v
```

Expected: `FileNotFoundError` または `FAILED` — スキーマファイルがまだ存在しない

- [ ] **Step 3: `orchestration/schema/state.schema.json` を作成する**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SDD state",
  "description": "Per-repository active SDD task state (.sdd/state.json).",
  "type": "object",
  "required": ["tier", "phase"],
  "additionalProperties": false,
  "properties": {
    "tier": {
      "type": "integer",
      "enum": [0, 1, 2],
      "description": "0 trivial, 1 small, 2 medium/large."
    },
    "phase": {
      "type": "string",
      "enum": ["brainstorm", "spec", "plan", "tasks", "implement", "verify", "done"],
      "description": "Current SDD phase."
    },
    "feature": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9-]*$",
      "description": "Active feature slug; matches specs/<feature>/."
    },
    "spec": {
      "type": "string",
      "description": "Path to the active spec directory."
    },
    "note": {
      "type": "string",
      "description": "Optional justification for Tier 0/1 exemption."
    }
  },
  "if": {
    "required": ["tier", "phase"],
    "properties": {
      "tier": { "const": 0 },
      "phase": { "const": "done" }
    }
  },
  "then": {},
  "else": { "required": ["feature"] }
}
```

- [ ] **Step 4: `orchestration/schema/tasks.schema.json` を更新する**

既存ファイルの `items` オブジェクトを以下で置き換える（`additionalProperties`, `required`, `properties` はそのままで `assigned_agent` と `blocked_reason` とルート `if/then/else` を変更）:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SDD Tasks",
  "description": "Full task state for all features in the project (.sdd/tasks.json). Kanban data source.",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["id", "phase", "status"],
    "additionalProperties": false,
    "properties": {
      "id": {
        "type": "string",
        "pattern": "^[a-z0-9][a-z0-9-]*$",
        "description": "Feature slug; matches specs/<id>/."
      },
      "phase": {
        "type": "string",
        "enum": ["brainstorm", "spec", "plan", "tasks", "implement", "verify", "done"]
      },
      "assigned_agent": {
        "type": ["string", "null"],
        "pattern": "^[a-z][a-z0-9-]*$",
        "description": "Agent that worked on this feature. Optional."
      },
      "status": {
        "type": "string",
        "enum": ["pending", "in_progress", "completed", "blocked"]
      },
      "handoff": {
        "type": ["string", "null"],
        "description": "Path to handoff.md, or null if not yet generated."
      },
      "blocked_reason": {
        "type": ["string", "null"],
        "minLength": 1,
        "description": "Non-empty string when status is 'blocked'. Null otherwise."
      }
    },
    "if": {
      "properties": { "status": { "const": "blocked" } },
      "required": ["status"]
    },
    "then": {
      "required": ["blocked_reason"],
      "properties": { "blocked_reason": { "type": "string", "minLength": 1 } }
    },
    "else": {
      "properties": { "blocked_reason": { "type": "null" } }
    }
  }
}
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
python3 -m pytest tests/test_sdd_validate.py -v
```

Expected: `8 passed`

- [ ] **Step 6: 全テストのリグレッションを確認する**

```bash
python3 -m pytest tests/ -q
```

Expected: `62 passed`（54 + 8）

- [ ] **Step 7: コミットする**

```bash
git add orchestration/schema/state.schema.json orchestration/schema/tasks.schema.json tests/test_sdd_validate.py
git commit -m "feat(validator): state/tasks JSON Schemaを追加・拡張する (#52)"
```

---

## Task 2: sdd-validate.py (CLI + check_schema_state + check_schema_tasks) + valid fixtures（SAC-3, SAC-4 partial, SAC-11）

**Files:**
- Create: `integration/ci/sdd-validate.py`
- Create: `tests/fixtures/valid-active/` (複数ファイル)
- Create: `tests/fixtures/valid-done/.sdd/state.json`
- Modify: `tests/test_sdd_validate.py`（関数テスト追記）

**Interfaces:**
- Produces:
  - `check_schema_state(root: Path) -> list[str]`
  - `check_schema_tasks(root: Path, feature: str) -> list[str]`
  - `SCHEMA_DIR: Path` — `orchestration/schema/` への絶対パス
  - `_load_json(path: Path) -> dict`
  - `_load_schema(name: str) -> dict`

- [ ] **Step 1: テストを追記する**

`tests/test_sdd_validate.py` 末尾に追加する:

```python
# ---------------------------------------------------------------------------
# Import sdd-validate.py (hyphen filename → importlib)
# ---------------------------------------------------------------------------

def _load_module():
    spec = importlib.util.spec_from_file_location(
        "sdd_validate",
        ROOT / "integration" / "ci" / "sdd-validate.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_v = _load_module()


# ---------------------------------------------------------------------------
# check_schema_state
# ---------------------------------------------------------------------------

def test_check_schema_state_valid_active(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "implement", "feature": "my-feature"})
    )
    assert _v.check_schema_state(tmp_path) == []


def test_check_schema_state_valid_done(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 0, "phase": "done"})
    )
    assert _v.check_schema_state(tmp_path) == []


def test_check_schema_state_missing_feature_error(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "implement"})
    )
    errors = _v.check_schema_state(tmp_path)
    assert len(errors) == 1


def test_check_schema_state_file_missing_error(tmp_path):
    errors = _v.check_schema_state(tmp_path)
    assert any("not found" in e for e in errors)


# ---------------------------------------------------------------------------
# check_schema_tasks
# ---------------------------------------------------------------------------

def test_check_schema_tasks_no_file_skips(tmp_path):
    assert _v.check_schema_tasks(tmp_path, "my-feature") == []


def test_check_schema_tasks_valid(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "tasks.json").write_text(json.dumps([
        {"id": "my-feature", "phase": "implement", "status": "in_progress",
         "handoff": None, "blocked_reason": None}
    ]))
    assert _v.check_schema_tasks(tmp_path, "my-feature") == []


def test_check_schema_tasks_feature_missing_in_tasks(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "tasks.json").write_text(json.dumps([
        {"id": "other-feature", "phase": "implement", "status": "in_progress",
         "handoff": None, "blocked_reason": None}
    ]))
    errors = _v.check_schema_tasks(tmp_path, "my-feature")
    assert any("my-feature" in e for e in errors)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python3 -m pytest tests/test_sdd_validate.py -k "check_schema" -v
```

Expected: `ModuleNotFoundError` または `FAILED` — `sdd-validate.py` がまだ存在しない

- [ ] **Step 3: `integration/ci/sdd-validate.py` を作成する**

```python
#!/usr/bin/env python3
"""SDD core validator.

exit 0 = all checks pass
exit 1 = validation error
exit 2 = internal error (fail-closed)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install -e '.[test]'", file=sys.stderr)
    sys.exit(2)

SCHEMA_DIR = Path(__file__).parent.parent.parent / "orchestration" / "schema"


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read {path}: {exc}") from exc


def _load_schema(name: str) -> dict:
    return _load_json(SCHEMA_DIR / name)


def _validate_schema(instance, schema: dict, label: str) -> list[str]:
    try:
        jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())
        return []
    except jsonschema.ValidationError as exc:
        return [f"{label}: {exc.message}"]


def check_schema_state(root: Path) -> list[str]:
    """Check 1: Validate .sdd/state.json against state.schema.json."""
    state_path = root / ".sdd" / "state.json"
    if not state_path.exists():
        return [f"state.json not found: {state_path}"]
    schema = _load_schema("state.schema.json")
    return _validate_schema(_load_json(state_path), schema, "state.json")


def check_schema_tasks(root: Path, feature: str) -> list[str]:
    """Check 2: Validate .sdd/tasks.json (skip if absent); error if active feature has no entry."""
    tasks_path = root / ".sdd" / "tasks.json"
    if not tasks_path.exists():
        return []
    schema = _load_schema("tasks.schema.json")
    tasks = _load_json(tasks_path)
    errors = _validate_schema(tasks, schema, "tasks.json")
    if errors:
        return errors
    if feature:
        ids = [t.get("id") for t in tasks]
        if feature not in ids:
            errors.append(f"tasks.json: no entry for feature '{feature}'")
    return errors


def check_schema_traceability(root: Path, feature: str) -> list[str]:
    """Check 3: Validate traceability.json (Tier 2 only)."""
    path = root / "specs" / feature / "traceability.json"
    if not path.exists():
        return [f"traceability.json not found: {path}"]
    schema = _load_schema("traceability.schema.json")
    return _validate_schema(_load_json(path), schema, "traceability.json")


def check_state_tasks_consistency(root: Path, feature: str) -> list[str]:
    """Check 4: state.json feature must have a matching entry in tasks.json."""
    tasks_path = root / ".sdd" / "tasks.json"
    if not tasks_path.exists():
        return []
    state = _load_json(root / ".sdd" / "state.json")
    tasks = _load_json(tasks_path)
    state_feature = state.get("feature", "")
    if not state_feature:
        return []
    entry_ids = [t.get("id") for t in tasks]
    if state_feature not in entry_ids:
        return [f"state.json feature='{state_feature}' has no matching entry in tasks.json"]
    return []


def check_tasks_md_consistency(root: Path, feature: str) -> list[str]:
    """Check 5: For phase=verify, all tasks.md checkboxes must be complete."""
    state = _load_json(root / ".sdd" / "state.json")
    if state.get("phase") != "verify":
        return []
    tasks_md = root / "specs" / feature / "tasks.md"
    if not tasks_md.exists():
        return [f"tasks.md not found: {tasks_md}"]
    errors = []
    for i, line in enumerate(tasks_md.read_text().splitlines(), 1):
        if re.match(r"\s*-\s*\[ \]", line):
            errors.append(f"tasks.md line {i}: unchecked item: {line.strip()}")
    return errors


def check_traceability_internal(root: Path, feature: str) -> list[str]:
    """Check 6: Duplicate spec_ac, task not in tasks.md, test file not found."""
    path = root / "specs" / feature / "traceability.json"
    if not path.exists():
        return [f"traceability.json not found: {path}"]
    data = _load_json(path)
    entries = data.get("entries", [])
    errors = []

    # Duplicate spec_ac
    spec_acs = [e["spec_ac"] for e in entries if e.get("spec_ac")]
    seen: set[str] = set()
    for ac in spec_acs:
        if ac in seen:
            errors.append(f"traceability.json: duplicate spec_ac '{ac}'")
        seen.add(ac)

    # Task references exist in tasks.md
    tasks_md = root / "specs" / feature / "tasks.md"
    if tasks_md.exists():
        tasks_md_text = tasks_md.read_text()
        for entry in entries:
            task = entry.get("task")
            if task and not re.search(
                rf"[-\s]\[.\]\s+{re.escape(task)}:", tasks_md_text
            ):
                errors.append(
                    f"traceability.json: task '{task}' not found in tasks.md"
                )

    # Test file existence (path before ::)
    for entry in entries:
        test = entry.get("test")
        if test and "::" in test:
            test_file = test.split("::")[0]
            if not (root / test_file).exists():
                errors.append(
                    f"traceability.json: test file not found: {test_file}"
                )

    return errors


def check_scope_out(root: Path, feature: str) -> list[str]:
    """Check 7: out-of-scope/deferred entries must have reason + HTTP(S) followup_issue."""
    path = root / "specs" / feature / "traceability.json"
    if not path.exists():
        return []
    data = _load_json(path)
    errors = []
    for entry in data.get("entries", []):
        if entry.get("status") in ("out-of-scope", "deferred"):
            ac = entry.get("issue_ac", "?")
            if not entry.get("reason"):
                errors.append(f"traceability.json: {ac} missing reason")
            followup = entry.get("followup_issue", "")
            if not followup or not re.match(r"^https?://", followup):
                errors.append(
                    f"traceability.json: {ac} missing HTTP(S) followup_issue"
                )
    return errors


def _resolve_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git rev-parse failed: {exc.stderr}", file=sys.stderr)
        sys.exit(2)


def main() -> None:  # noqa: C901
    parser = argparse.ArgumentParser(description="SDD core validator")
    parser.add_argument("--root", type=Path, help="Repository root")
    parser.add_argument("--feature", type=str, help="Feature slug")
    args = parser.parse_args()

    try:
        root = args.root or _resolve_root()
        state_path = root / ".sdd" / "state.json"

        # Check 1: state schema (always)
        errors = check_schema_state(root)
        if errors:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        state = _load_json(state_path)
        tier = state.get("tier", -1)
        phase = state.get("phase", "")

        # done-reset: skip feature checks
        if tier == 0 and phase == "done":
            print("sdd-validate: tier=0 phase=done — feature checks skipped. PASS")
            sys.exit(0)

        feature = args.feature or state.get("feature", "")
        if not feature:
            print("ERROR: no feature in state.json and --feature not provided", file=sys.stderr)
            sys.exit(1)

        all_errors: list[str] = []

        # Check 2: tasks schema
        all_errors.extend(check_schema_tasks(root, feature))

        # Check 3: traceability schema (Tier 2)
        if tier == 2:
            all_errors.extend(check_schema_traceability(root, feature))

        # Check 4: state/tasks consistency
        all_errors.extend(check_state_tasks_consistency(root, feature))

        # Check 5: tasks.md consistency (phase=verify)
        all_errors.extend(check_tasks_md_consistency(root, feature))

        # Check 6: traceability internal (Tier 2)
        if tier == 2:
            all_errors.extend(check_traceability_internal(root, feature))

        # Check 7: scope-out (Tier 2)
        if tier == 2:
            all_errors.extend(check_scope_out(root, feature))

        if all_errors:
            for e in all_errors:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"sdd-validate: all checks passed for feature '{feature}'")

    except SystemExit:
        raise
    except Exception as exc:  # fail-closed
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: valid fixtures を作成する**

`tests/fixtures/valid-active/` の構造:

```
tests/fixtures/valid-active/
  .sdd/
    state.json
    tasks.json
  specs/
    my-feature/
      tasks.md
      traceability.json
  tests/
    test_my_feature.py
```

各ファイルの内容:

**`.sdd/state.json`**:
```json
{"tier": 2, "phase": "implement", "feature": "my-feature"}
```

**`.sdd/tasks.json`**:
```json
[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

**`specs/my-feature/tasks.md`**:
```markdown
# Tasks: my-feature
- [x] T1: do something. AC: SAC-1
```

**`specs/my-feature/traceability.json`**:
```json
{
  "issue": 99,
  "issue_url": "https://github.com/owner/repo/issues/99",
  "feature": "my-feature",
  "entries": [
    {
      "issue_ac": "99-AC1",
      "spec_ac": "SAC-1",
      "task": "T1",
      "test": "tests/test_my_feature.py::test_something",
      "status": "in-scope"
    }
  ]
}
```

**`tests/test_my_feature.py`**:
```python
def test_something():
    assert True
```

`tests/fixtures/valid-done/` の構造:

**`.sdd/state.json`**:
```json
{"tier": 0, "phase": "done", "note": "no active feature"}
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
python3 -m pytest tests/test_sdd_validate.py -k "check_schema" -v
```

Expected: `11 passed`（schema 8 + check_schema 新規 3）

実際の新規テスト件数:
- `test_check_schema_state_valid_active` — 1
- `test_check_schema_state_valid_done` — 1
- `test_check_schema_state_missing_feature_error` — 1
- `test_check_schema_state_file_missing_error` — 1
- `test_check_schema_tasks_no_file_skips` — 1
- `test_check_schema_tasks_valid` — 1
- `test_check_schema_tasks_feature_missing_in_tasks` — 1

Expected: `15 passed`（schema 8 + check_schema_state 4 + check_schema_tasks 3）

- [ ] **Step 6: 全テストを実行する**

```bash
python3 -m pytest tests/ -q
```

Expected: `69 passed`（54 + 15）

- [ ] **Step 7: コミットする**

```bash
git add integration/ci/sdd-validate.py tests/test_sdd_validate.py tests/fixtures/valid-active/ tests/fixtures/valid-done/
git commit -m "feat(validator): sdd-validate.pyのCLIとschema検査2関数を追加する (#52)"
```

---

## Task 3: check_state_tasks_consistency + check_tasks_md_consistency + 関連 fixtures（SAC-7）

**Files:**
- Modify: `tests/test_sdd_validate.py`（テスト追記）
- Create: `tests/fixtures/invalid-state-mismatch/`
- Create: `tests/fixtures/invalid-tasks-incomplete/`

**Interfaces:**
- Consumes: Task 2 で定義した `check_state_tasks_consistency`, `check_tasks_md_consistency` 関数
- Produces: これらの関数のテストカバレッジ

- [ ] **Step 1: テストを追記する**

`tests/test_sdd_validate.py` 末尾に追加する:

```python
# ---------------------------------------------------------------------------
# check_state_tasks_consistency
# ---------------------------------------------------------------------------

def test_check_state_tasks_consistency_no_tasks_file(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "implement", "feature": "foo"})
    )
    assert _v.check_state_tasks_consistency(tmp_path, "foo") == []


def test_check_state_tasks_consistency_match(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "implement", "feature": "foo"})
    )
    (tmp_path / ".sdd" / "tasks.json").write_text(json.dumps([
        {"id": "foo", "phase": "implement", "status": "in_progress",
         "handoff": None, "blocked_reason": None}
    ]))
    assert _v.check_state_tasks_consistency(tmp_path, "foo") == []


def test_check_state_tasks_consistency_mismatch(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "implement", "feature": "foo"})
    )
    (tmp_path / ".sdd" / "tasks.json").write_text(json.dumps([
        {"id": "bar", "phase": "implement", "status": "in_progress",
         "handoff": None, "blocked_reason": None}
    ]))
    errors = _v.check_state_tasks_consistency(tmp_path, "foo")
    assert any("foo" in e for e in errors)


# ---------------------------------------------------------------------------
# check_tasks_md_consistency
# ---------------------------------------------------------------------------

def test_check_tasks_md_not_verify_skips(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "implement", "feature": "foo"})
    )
    assert _v.check_tasks_md_consistency(tmp_path, "foo") == []


def test_check_tasks_md_all_checked(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "verify", "feature": "foo"})
    )
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    (tmp_path / "specs" / "foo" / "tasks.md").write_text(
        "# Tasks\n- [x] T1: done task. AC: SAC-1\n"
    )
    assert _v.check_tasks_md_consistency(tmp_path, "foo") == []


def test_check_tasks_md_unchecked_item_error(tmp_path):
    (tmp_path / ".sdd").mkdir()
    (tmp_path / ".sdd" / "state.json").write_text(
        json.dumps({"tier": 2, "phase": "verify", "feature": "foo"})
    )
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    (tmp_path / "specs" / "foo" / "tasks.md").write_text(
        "# Tasks\n- [ ] T1: incomplete task. AC: SAC-1\n"
    )
    errors = _v.check_tasks_md_consistency(tmp_path, "foo")
    assert any("unchecked" in e for e in errors)
```

- [ ] **Step 2: テストが通ることを確認する（関数はTask 2で実装済み）**

```bash
python3 -m pytest tests/test_sdd_validate.py -k "consistency or tasks_md" -v
```

Expected: `7 passed`

- [ ] **Step 3: invalid fixtures を作成する**

`tests/fixtures/invalid-state-mismatch/`:

**`.sdd/state.json`**:
```json
{"tier": 2, "phase": "implement", "feature": "feature-a"}
```

**`.sdd/tasks.json`**:
```json
[{"id": "feature-b", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

`tests/fixtures/invalid-tasks-incomplete/`:

**`.sdd/state.json`**:
```json
{"tier": 2, "phase": "verify", "feature": "my-feature"}
```

**`.sdd/tasks.json`**:
```json
[{"id": "my-feature", "phase": "verify", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

**`specs/my-feature/tasks.md`**:
```markdown
# Tasks: my-feature
- [x] T1: completed task. AC: SAC-1
- [ ] T2: incomplete task. AC: SAC-2
```

**`specs/my-feature/traceability.json`**:
```json
{
  "issue": 99,
  "issue_url": "https://github.com/owner/repo/issues/99",
  "feature": "my-feature",
  "entries": [
    {
      "issue_ac": "99-AC1",
      "spec_ac": "SAC-1",
      "task": "T1",
      "test": "tests/test_my_feature.py::test_something",
      "status": "in-scope"
    }
  ]
}
```

**`tests/test_my_feature.py`**（ファイルが存在することが必要）:
```python
def test_something():
    assert True
```

- [ ] **Step 4: 全テストを実行する**

```bash
python3 -m pytest tests/ -q
```

Expected: `76 passed`（69 + 7）

- [ ] **Step 5: コミットする**

```bash
git add tests/test_sdd_validate.py tests/fixtures/invalid-state-mismatch/ tests/fixtures/invalid-tasks-incomplete/
git commit -m "feat(validator): state/tasks整合性とtasks.md検査のテストとfixtureを追加する (#52)"
```

---

## Task 4: check_schema_traceability + check_traceability_internal + check_scope_out + fixture（SAC-8, SAC-9）

**Files:**
- Modify: `tests/test_sdd_validate.py`（テスト追記）
- Create: `tests/fixtures/invalid-traceability/`

**Interfaces:**
- Consumes: Task 2 で定義した `check_schema_traceability`, `check_traceability_internal`, `check_scope_out` 関数
- Produces: これらの関数のテストカバレッジ

- [ ] **Step 1: テストを追記する**

`tests/test_sdd_validate.py` 末尾に追加する:

```python
# ---------------------------------------------------------------------------
# check_schema_traceability
# ---------------------------------------------------------------------------

def test_check_schema_traceability_valid(tmp_path):
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    (tmp_path / "specs" / "foo" / "traceability.json").write_text(json.dumps({
        "issue": 99,
        "issue_url": "https://github.com/owner/repo/issues/99",
        "feature": "foo",
        "entries": [{
            "issue_ac": "99-AC1", "spec_ac": "SAC-1",
            "task": "T1", "test": "tests/test_foo.py::test_a",
            "status": "in-scope"
        }]
    }))
    assert _v.check_schema_traceability(tmp_path, "foo") == []


def test_check_schema_traceability_file_missing(tmp_path):
    errors = _v.check_schema_traceability(tmp_path, "foo")
    assert any("not found" in e for e in errors)


def test_check_schema_traceability_invalid_schema(tmp_path):
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    # entries が空 → minItems: 1 に違反
    (tmp_path / "specs" / "foo" / "traceability.json").write_text(json.dumps({
        "issue": 99,
        "issue_url": "https://github.com/owner/repo/issues/99",
        "feature": "foo",
        "entries": []
    }))
    errors = _v.check_schema_traceability(tmp_path, "foo")
    assert len(errors) == 1


# ---------------------------------------------------------------------------
# check_traceability_internal
# ---------------------------------------------------------------------------

def _make_traceability_fixture(tmp_path, entries):
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    (tmp_path / "specs" / "foo" / "traceability.json").write_text(json.dumps({
        "issue": 99,
        "issue_url": "https://github.com/owner/repo/issues/99",
        "feature": "foo",
        "entries": entries,
    }))
    (tmp_path / "specs" / "foo" / "tasks.md").write_text(
        "# Tasks\n- [x] T1: done. AC: SAC-1\n"
    )


def test_check_traceability_internal_valid(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("def test_a(): pass")
    _make_traceability_fixture(tmp_path, [{
        "issue_ac": "99-AC1", "spec_ac": "SAC-1",
        "task": "T1", "test": "tests/test_foo.py::test_a",
        "status": "in-scope"
    }])
    assert _v.check_traceability_internal(tmp_path, "foo") == []


def test_check_traceability_internal_duplicate_spec_ac(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("def test_a(): pass")
    _make_traceability_fixture(tmp_path, [
        {"issue_ac": "99-AC1", "spec_ac": "SAC-1",
         "task": "T1", "test": "tests/test_foo.py::test_a", "status": "in-scope"},
        {"issue_ac": "99-AC2", "spec_ac": "SAC-1",  # duplicate SAC-1
         "task": "T1", "test": "tests/test_foo.py::test_a", "status": "in-scope"},
    ])
    errors = _v.check_traceability_internal(tmp_path, "foo")
    assert any("duplicate" in e for e in errors)


def test_check_traceability_internal_missing_test_file(tmp_path):
    _make_traceability_fixture(tmp_path, [{
        "issue_ac": "99-AC1", "spec_ac": "SAC-1",
        "task": "T1", "test": "tests/test_nonexistent.py::test_a",
        "status": "in-scope"
    }])
    errors = _v.check_traceability_internal(tmp_path, "foo")
    assert any("test_nonexistent.py" in e for e in errors)


def test_check_traceability_internal_missing_task(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("def test_a(): pass")
    _make_traceability_fixture(tmp_path, [{
        "issue_ac": "99-AC1", "spec_ac": "SAC-1",
        "task": "T99",  # T99 は tasks.md に存在しない
        "test": "tests/test_foo.py::test_a", "status": "in-scope"
    }])
    errors = _v.check_traceability_internal(tmp_path, "foo")
    assert any("T99" in e for e in errors)


# ---------------------------------------------------------------------------
# check_scope_out
# ---------------------------------------------------------------------------

def test_check_scope_out_no_out_of_scope(tmp_path):
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    (tmp_path / "specs" / "foo" / "traceability.json").write_text(json.dumps({
        "issue": 99, "issue_url": "https://github.com/o/r/issues/99",
        "feature": "foo",
        "entries": [{"issue_ac": "99-AC1", "spec_ac": "SAC-1",
                      "task": "T1", "test": "tests/t.py::test_a", "status": "in-scope"}]
    }))
    assert _v.check_scope_out(tmp_path, "foo") == []


def test_check_scope_out_valid_out_of_scope(tmp_path):
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    (tmp_path / "specs" / "foo" / "traceability.json").write_text(json.dumps({
        "issue": 99, "issue_url": "https://github.com/o/r/issues/99",
        "feature": "foo",
        "entries": [{
            "issue_ac": "99-AC1", "spec_ac": None, "task": None, "test": None,
            "status": "out-of-scope",
            "reason": "out of scope for this feature",
            "followup_issue": "https://github.com/o/r/issues/100"
        }]
    }))
    assert _v.check_scope_out(tmp_path, "foo") == []


def test_check_scope_out_missing_followup(tmp_path):
    (tmp_path / "specs" / "foo").mkdir(parents=True)
    (tmp_path / "specs" / "foo" / "traceability.json").write_text(json.dumps({
        "issue": 99, "issue_url": "https://github.com/o/r/issues/99",
        "feature": "foo",
        "entries": [{
            "issue_ac": "99-AC1", "spec_ac": None, "task": None, "test": None,
            "status": "out-of-scope",
            "reason": "out of scope",
            "followup_issue": "mailto:bad@example.com"  # HTTPSでない
        }]
    }))
    errors = _v.check_scope_out(tmp_path, "foo")
    assert any("followup_issue" in e for e in errors)
```

- [ ] **Step 2: テストが通ることを確認する（関数はTask 2で実装済み）**

```bash
python3 -m pytest tests/test_sdd_validate.py -k "traceability or scope_out" -v
```

Expected: `12 passed`

- [ ] **Step 3: invalid-traceability fixture を作成する**

`tests/fixtures/invalid-traceability/`:

**`.sdd/state.json`**:
```json
{"tier": 2, "phase": "implement", "feature": "my-feature"}
```

**`.sdd/tasks.json`**:
```json
[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

**`specs/my-feature/tasks.md`**:
```markdown
# Tasks: my-feature
- [x] T1: completed task. AC: SAC-1
```

**`specs/my-feature/traceability.json`**（重複 SAC-1 + 存在しないテストファイル）:
```json
{
  "issue": 99,
  "issue_url": "https://github.com/owner/repo/issues/99",
  "feature": "my-feature",
  "entries": [
    {
      "issue_ac": "99-AC1",
      "spec_ac": "SAC-1",
      "task": "T1",
      "test": "tests/test_nonexistent.py::test_something",
      "status": "in-scope"
    },
    {
      "issue_ac": "99-AC2",
      "spec_ac": "SAC-1",
      "task": "T1",
      "test": "tests/test_nonexistent.py::test_other",
      "status": "in-scope"
    }
  ]
}
```

- [ ] **Step 4: 全テストを実行する**

```bash
python3 -m pytest tests/ -q
```

Expected: `88 passed`（76 + 12）

- [ ] **Step 5: コミットする**

```bash
git add tests/test_sdd_validate.py tests/fixtures/invalid-traceability/
git commit -m "feat(validator): traceability検査とscope-out検査のテストとfixtureを追加する (#52)"
```

---

## Task 5: sdd-validate.sh + sdd-validate-hook.sh + sdd-check.yml + fail-closed テスト（SAC-3, SAC-5, SAC-6, SAC-10）

**Files:**
- Create: `integration/ci/sdd-validate.sh`
- Create: `integration/hooks/sdd-validate-hook.sh`
- Modify: `integration/ci/sdd-check.yml`
- Modify: `tests/test_sdd_validate.py`（subprocess テスト追記）

**Interfaces:**
- Consumes: `integration/ci/sdd-validate.py`（Task 2 で作成）
- Produces: shell スクリプト 2 件 + CI 設定

- [ ] **Step 1: テストを追記する**

`tests/test_sdd_validate.py` 末尾に追加する:

```python
# ---------------------------------------------------------------------------
# Shell integration tests (subprocess)
# ---------------------------------------------------------------------------

import subprocess as _subprocess


def _run_sh(fixture_name: str, extra_args: list[str] | None = None) -> _subprocess.CompletedProcess:
    sh = ROOT / "integration" / "ci" / "sdd-validate.sh"
    root = FIXTURES / fixture_name
    cmd = ["bash", str(sh), "--root", str(root)] + (extra_args or [])
    return _subprocess.run(cmd, capture_output=True, text=True)


def test_sh_valid_active_exits_0():
    result = _run_sh("valid-active")
    assert result.returncode == 0


def test_sh_valid_done_exits_0():
    result = _run_sh("valid-done")
    assert result.returncode == 0


def test_sh_invalid_state_mismatch_exits_1():
    result = _run_sh("invalid-state-mismatch")
    assert result.returncode == 1


def test_sh_invalid_traceability_exits_1():
    result = _run_sh("invalid-traceability")
    assert result.returncode == 1


def test_sh_invalid_tasks_incomplete_exits_1():
    result = _run_sh("invalid-tasks-incomplete")
    assert result.returncode == 1


def test_sh_missing_state_json_exits_1(tmp_path):
    sh = ROOT / "integration" / "ci" / "sdd-validate.sh"
    result = _subprocess.run(
        ["bash", str(sh), "--root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python3 -m pytest tests/test_sdd_validate.py -k "sh_" -v
```

Expected: `FAILED` — `sdd-validate.sh` がまだ存在しない

- [ ] **Step 3: `integration/ci/sdd-validate.sh` を作成する**

```bash
#!/usr/bin/env bash
# Thin wrapper — resolves sdd-validate.py relative to this script (cwd-independent).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/sdd-validate.py" "$@"
```

実行権限を付与する:
```bash
chmod +x integration/ci/sdd-validate.sh
```

- [ ] **Step 4: `integration/hooks/sdd-validate-hook.sh` を作成する**

```bash
#!/usr/bin/env bash
# Freeze gate hook — calls sdd-validate.sh with repo root.
# Usage: sdd-validate-hook.sh [--root <path>] [extra args...]
# If --root is provided as first arg, pass all args through.
# Otherwise, resolve root via git rev-parse (fail-closed on error).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "${1:-}" = "--root" ]; then
  exec bash "$SCRIPT_DIR/../ci/sdd-validate.sh" "$@"
fi
exec bash "$SCRIPT_DIR/../ci/sdd-validate.sh" \
  --root "$(git rev-parse --show-toplevel)"
```

実行権限を付与する:
```bash
chmod +x integration/hooks/sdd-validate-hook.sh
```

- [ ] **Step 5: `integration/ci/sdd-check.yml` を更新する**

既存の `sdd:` ジョブ内、`- uses: actions/checkout@v4` の後に以下を追加する:

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e ".[test]"

      - name: Run sdd-validate
        run: bash integration/ci/sdd-validate.sh --root .
```

`sdd-check.yml` の `sdd:` ジョブ末尾に追加する形にする（既存の State reset gate・Spec gate・Tests ステップを残す）。

- [ ] **Step 6: テストが通ることを確認する**

```bash
python3 -m pytest tests/test_sdd_validate.py -k "sh_" -v
```

Expected: `6 passed`

- [ ] **Step 7: 全テストを実行する**

```bash
python3 -m pytest tests/ -q
```

Expected: `94 passed`（88 + 6）

- [ ] **Step 8: コミットする**

```bash
git add integration/ci/sdd-validate.sh integration/hooks/sdd-validate-hook.sh integration/ci/sdd-check.yml tests/test_sdd_validate.py
git commit -m "feat(validator): sdd-validate.shとhookとCI統合を追加する (#52)"
```

---

## 完了の定義

- [ ] `python3 -m pytest tests/test_sdd_validate.py` が全件 PASS
- [ ] `python3 -m pytest tests/` が全件 PASS（リグレッションなし）
- [ ] CI green
- [ ] sdd-reviewer 合格（SAC-1〜SAC-11）
