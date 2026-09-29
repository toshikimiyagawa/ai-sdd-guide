# Negative Fixtures for SDD Validator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 14 negative fixture directories (+ 14 valid counterparts) and a pytest test file that proves `sdd-validate.py` detects each validator failure pattern with RED/GREEN tests.

**Architecture:** Static fixture directories under `tests/fixtures/fixture-*/` (negative) and `tests/fixtures/fixture-*-valid/` (valid). Each directory is a self-contained repo root passable to `--root`. A new `tests/test_negative_fixtures.py` uses subprocess to run `sdd-validate.sh` and assert exit codes + error fragments.

**Tech Stack:** Python / pytest, bash, `integration/ci/sdd-validate.py`, `jsonschema`

**Spec:** `_dev/specs/2026-09-29-negative-fixtures-design.md`

## Global Constraints

- Feature slug: `negative-tests` (`specs/negative-tests/`)
- Fixture feature slug inside fixtures: `my-feature` (consistent with existing fixtures)
- Issue number inside fixtures: `99` (dummy, consistent with existing fixtures)
- All fixture paths: `tests/fixtures/fixture-<name>/` (negative) and `tests/fixtures/fixture-<name>-valid/` (valid)
- Test file: `tests/test_negative_fixtures.py` — do NOT modify existing `test_sdd_validate.py`
- Validator entrypoint: `integration/ci/sdd-validate.sh` (wraps sdd-validate.py)
- Valid fixture evidence.json: use placeholder SHA `"0000000000000000000000000000000000000000"` in static files; the test helper injects a real SHA at test time
- Every negative fixture README.md: include re-run commands, check number, expected error fragment
- Every commit: reference `#47`

## Review Focus

- `fixture-wrong-state` vs `fixture-missing-tasks-entry` — both can produce "no entry" style errors from two different check functions; ensure the parametrize `expected_fragment` is specific enough to distinguish them
- `fixture-stale-snapshot-hash` — body_hash mismatch error message must match the exact string the validator prints; verify against `check_issue_snapshot` source before writing the test fragment
- Valid evidence fixtures require a real 40-char git SHA; if `git rev-parse HEAD` fails in CI (shallow clone), the test will fail; add `skipif` if the git check fails
- `fixture-non-test-count` / `fixture-missing-test-count` — these are JSON schema failures, not logic checks; the error message comes from jsonschema and contains "test_count"; confirm the fragment matches
- Fixture directories with `specs/my-feature/spec.md` must define `SAC-1` and `SAC-2` as literal strings (the pattern `\bSAC-\d+\b` is used by `check_traceability_internal` to find defined ACs)

---

## File Map

**New files (fixtures):**
```
tests/fixtures/
  fixture-incomplete-tasks/                   # negative: unchecked task in verify
  fixture-incomplete-tasks-valid/
  fixture-wrong-state/                        # negative: state.feature not in tasks.json
  fixture-wrong-state-valid/
  fixture-missing-tasks-entry/                # negative: tasks.json empty (no feature entry)
  fixture-missing-tasks-entry-valid/
  fixture-phase-mismatch/                     # negative: state.phase ≠ tasks.json phase
  fixture-phase-mismatch-valid/
  fixture-no-test-mapping/                    # negative: test file referenced but absent
  fixture-no-test-mapping-valid/
  fixture-orphan-spec-ac/                     # negative: spec_ac not in spec.md
  fixture-orphan-spec-ac-valid/
  fixture-duplicate-spec-ac/                  # negative: duplicate spec_ac in traceability
  fixture-duplicate-spec-ac-valid/
  fixture-scope-out-no-followup/              # negative: out-of-scope without followup URL
  fixture-scope-out-no-followup-valid/
  fixture-weakened-ac/                        # negative: snapshot AC not in traceability
  fixture-weakened-ac-valid/
  fixture-stale-snapshot-hash/                # negative: body_hash stale after raw_body edit
  fixture-stale-snapshot-hash-valid/
  fixture-untracked-issue-ac/                 # negative: traceability AC not in snapshot
  fixture-untracked-issue-ac-valid/
  fixture-invalid-evidence-commit/            # negative: commit_sha not in git
  fixture-invalid-evidence-commit-valid/
  fixture-non-test-count/                     # negative: lint entry has test_count (schema violation)
  fixture-non-test-count-valid/
  fixture-missing-test-count/                 # negative: test entry missing test_count (schema violation)
  fixture-missing-test-count-valid/
```

**New test file:**
```
tests/test_negative_fixtures.py
```

**New SDD spec artifacts:**
```
specs/negative-tests/spec.md
specs/negative-tests/plan.md
specs/negative-tests/tasks.md
specs/negative-tests/traceability.json
specs/negative-tests/issue-snapshot.json
specs/negative-tests/handoff.md
```

---

## Shared fixture templates

Every fixture in this plan uses the following base files unless the task says otherwise.

### Base `spec.md` (for fixtures needing spec.md)
```markdown
# Spec: my-feature

## Acceptance Criteria

- SAC-1: first criterion works
- SAC-2: second criterion works
```

### Base `traceability.json` (valid, complete — for valid fixtures)
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
    },
    {
      "issue_ac": "99-AC2",
      "spec_ac": "SAC-2",
      "task": "T2",
      "test": "tests/test_my_feature.py::test_something_else",
      "status": "in-scope"
    }
  ]
}
```

### Base `issue-snapshot.json` (valid)
```json
{
  "issue": 99,
  "url": "https://github.com/owner/repo/issues/99",
  "fetched_at": "2026-09-29T00:00:00Z",
  "raw_body": "## 受入条件\n\n- [ ] first criterion works\n- [ ] second criterion works\n",
  "body_hash": "COMPUTE_BELOW",
  "stable_acs": [
    {"id": "99-AC1", "text": "first criterion works"},
    {"id": "99-AC2", "text": "second criterion works"}
  ]
}
```

Compute `body_hash` by running:
```bash
python3 -c "
import hashlib
raw = '## 受入条件\n\n- [ ] first criterion works\n- [ ] second criterion works\n'
print(hashlib.sha256(raw.encode('utf-8')).hexdigest())
"
```
Result: `0e9cc93e6d0e5c2c0d87a643b36e8cd22fcad4f1a9b78d01b0dbb8dc37c7b4a4`

So the body_hash value to use: `"0e9cc93e6d0e5c2c0d87a643b36e8cd22fcad4f1a9b78d01b0dbb8dc37c7b4a4"`

### Base `evidence.json` (valid — SHA injected at test time)
```json
{
  "feature": "my-feature",
  "commit_sha": "0000000000000000000000000000000000000000",
  "entries": [
    {
      "command_type": "test",
      "command": "pytest tests/test_my_feature.py",
      "result": "2 passed",
      "test_count": 2
    }
  ]
}
```

### Base `tests/test_my_feature.py` (placeholder, must exist for traceability test references)
```python
def test_something():
    pass

def test_something_else():
    pass
```

### Base `tasks.md` (all complete — for valid fixtures in verify phase)
```markdown
# Tasks: my-feature
- [x] T1: first task. AC: SAC-1
- [x] T2: second task. AC: SAC-2
```

### Base `tasks.json`
```json
[
  {
    "id": "my-feature",
    "phase": "verify",
    "status": "in_progress",
    "handoff": null,
    "blocked_reason": null
  }
]
```

---

## Task T1: Test harness + `fixture-incomplete-tasks` pair

**Files:**
- Create: `tests/test_negative_fixtures.py`
- Create: `tests/fixtures/fixture-incomplete-tasks/.sdd/state.json`
- Create: `tests/fixtures/fixture-incomplete-tasks/.sdd/tasks.json`
- Create: `tests/fixtures/fixture-incomplete-tasks/specs/my-feature/tasks.md`
- Create: `tests/fixtures/fixture-incomplete-tasks/specs/my-feature/traceability.json`
- Create: `tests/fixtures/fixture-incomplete-tasks/specs/my-feature/spec.md`
- Create: `tests/fixtures/fixture-incomplete-tasks/README.md`
- Create: `tests/fixtures/fixture-incomplete-tasks-valid/` (all 7 files: state, tasks.json, spec.md, traceability.json, issue-snapshot.json, evidence.json, tests/test_my_feature.py, tasks.md, README.md)

**Interfaces:**
- Produces: `FIXTURES`, `_run_validator(fixture_name)`, `_prepare_valid_fixture(fixture_name, tmp_path)` helpers; `test_negative_fixture_fails` and `test_valid_fixture_passes` parametrized tests

- [ ] **Step 1: Write the failing test (scaffold)**

Create `tests/test_negative_fixtures.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails (fixture files don't exist yet)**

```bash
pytest tests/test_negative_fixtures.py -v
```
Expected: `FileNotFoundError` or `FAILED` because fixture dirs don't exist yet.

- [ ] **Step 3: Create `fixture-incomplete-tasks/` negative fixture**

`.sdd/state.json`:
```json
{"tier": 2, "phase": "verify", "feature": "my-feature"}
```

`.sdd/tasks.json`:
```json
[{"id": "my-feature", "phase": "verify", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

`specs/my-feature/spec.md`: (base spec.md from Shared Templates above)

`specs/my-feature/tasks.md`:
```markdown
# Tasks: my-feature
- [x] T1: first task. AC: SAC-1
- [ ] T2: second task — INTENTIONALLY INCOMPLETE. AC: SAC-2
```

`specs/my-feature/traceability.json`: (base traceability.json from Shared Templates — test file path can be non-existent, the test checks for the unchecked-task error first and that's what matters)

`README.md`:
```markdown
## fixture-incomplete-tasks

**再現パターン:** `phase=verify` のときに `tasks.md` に未完了 checkbox が残っている。

**対応チェック:** Check 5 — `check_tasks_md_consistency`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-incomplete-tasks
# → exit 1, stderr に "unchecked item" が含まれる
```

**GREEN確認コマンド (valid版):**
```bash
# tmp にコピーして evidence.json の SHA を実 HEAD に差し替えてから実行
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-incomplete-tasks-valid
# → exit 0
```
```

- [ ] **Step 4: Create `fixture-incomplete-tasks-valid/` valid fixture**

`.sdd/state.json`:
```json
{"tier": 2, "phase": "verify", "feature": "my-feature"}
```

`.sdd/tasks.json`:
```json
[{"id": "my-feature", "phase": "verify", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

`specs/my-feature/spec.md`: (base spec.md)

`specs/my-feature/tasks.md`:
```markdown
# Tasks: my-feature
- [x] T1: first task. AC: SAC-1
- [x] T2: second task. AC: SAC-2
```

`specs/my-feature/traceability.json`: (base traceability.json)

`specs/my-feature/issue-snapshot.json`:
```json
{
  "issue": 99,
  "url": "https://github.com/owner/repo/issues/99",
  "fetched_at": "2026-09-29T00:00:00Z",
  "raw_body": "## 受入条件\n\n- [ ] first criterion works\n- [ ] second criterion works\n",
  "body_hash": "0e9cc93e6d0e5c2c0d87a643b36e8cd22fcad4f1a9b78d01b0dbb8dc37c7b4a4",
  "stable_acs": [
    {"id": "99-AC1", "text": "first criterion works"},
    {"id": "99-AC2", "text": "second criterion works"}
  ]
}
```

`specs/my-feature/evidence.json`: (base evidence.json — SHA placeholder injected at test time)

`tests/test_my_feature.py`: (base test_my_feature.py)

`README.md`:
```markdown
## fixture-incomplete-tasks-valid

valid版。`tasks.md` のすべての checkbox が完了している。
`evidence.json` の `commit_sha` はテスト実行時に real HEAD SHA へ置換される。
```

- [ ] **Step 5: Run test to verify RED/GREEN**

```bash
pytest tests/test_negative_fixtures.py -v
```
Expected: Both parametrize cases PASS (RED=exit 1 detected, GREEN=exit 0 from valid fixture).

- [ ] **Step 6: Commit**

```bash
git add tests/test_negative_fixtures.py tests/fixtures/fixture-incomplete-tasks tests/fixtures/fixture-incomplete-tasks-valid
git commit -m "test(negative-fixtures): fixture-incomplete-tasks RED/GREEN (#47)"
```

---

## Task T2: State/tasks consistency fixtures

**Fixtures:** `fixture-wrong-state`, `fixture-missing-tasks-entry`, `fixture-phase-mismatch` (+ valid counterparts)

**Files:** 9 fixture dirs (3 negative + 3 valid), each with 4-6 files; update `NEGATIVE_CASES` and `VALID_CASES` in `test_negative_fixtures.py`

**Interfaces:**
- Consumes: `_run_validator`, `_prepare_valid_fixture` from T1
- Produces: 3 more negative + 3 more valid parametrize cases

- [ ] **Step 1: Create `fixture-wrong-state/`**

`.sdd/state.json`:
```json
{"tier": 2, "phase": "implement", "feature": "other-feature"}
```

`.sdd/tasks.json`:
```json
[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

No `specs/` needed (error fires before feature-specific checks matter).

`README.md`:
```markdown
## fixture-wrong-state

**再現パターン:** `state.json` の `feature` が `tasks.json` に存在しないfeatureを指している。

**対応チェック:** Check 4 — `check_state_tasks_consistency`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-wrong-state
# → exit 1, stderr に "no matching entry" が含まれる
```
```

- [ ] **Step 2: Create `fixture-missing-tasks-entry/`**

`.sdd/state.json`:
```json
{"tier": 2, "phase": "implement", "feature": "my-feature"}
```

`.sdd/tasks.json`:
```json
[]
```

`README.md`:
```markdown
## fixture-missing-tasks-entry

**再現パターン:** `tasks.json` が空で active feature のエントリがない。

**対応チェック:** Check 2 — `check_schema_tasks`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-missing-tasks-entry
# → exit 1, stderr に "no entry for feature" が含まれる
```
```

- [ ] **Step 3: Create `fixture-phase-mismatch/`**

`.sdd/state.json`:
```json
{"tier": 2, "phase": "implement", "feature": "my-feature"}
```

`.sdd/tasks.json`:
```json
[{"id": "my-feature", "phase": "verify", "status": "in_progress", "handoff": null, "blocked_reason": null}]
```

`README.md`:
```markdown
## fixture-phase-mismatch

**再現パターン:** `state.json` の `phase` と `tasks.json` エントリの `phase` が不一致。

**対応チェック:** Check 4 — `check_state_tasks_consistency`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-phase-mismatch
# → exit 1, stderr に "does not match tasks.json entry" が含まれる
```
```

- [ ] **Step 4: Create valid counterparts**

`fixture-wrong-state-valid/`:
- `.sdd/state.json`: `{"tier": 2, "phase": "implement", "feature": "my-feature"}`
- `.sdd/tasks.json`: `[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]`
- `specs/my-feature/spec.md`: base spec.md
- `specs/my-feature/traceability.json`: base traceability.json
- `specs/my-feature/issue-snapshot.json`: base issue-snapshot.json (with body_hash `0e9cc93e6d0e5c2c0d87a643b36e8cd22fcad4f1a9b78d01b0dbb8dc37c7b4a4`)
- `specs/my-feature/evidence.json`: base evidence.json (SHA placeholder)
- `tests/test_my_feature.py`: base test file

`fixture-missing-tasks-entry-valid/`: same as `fixture-wrong-state-valid/`

`fixture-phase-mismatch-valid/`: same but both state.json and tasks.json.phase = `"implement"`

- [ ] **Step 5: Update `NEGATIVE_CASES` and `VALID_CASES` in `test_negative_fixtures.py`**

```python
NEGATIVE_CASES = [
    ("fixture-incomplete-tasks",    "unchecked item"),
    ("fixture-wrong-state",         "no matching entry"),
    ("fixture-missing-tasks-entry", "no entry for feature"),
    ("fixture-phase-mismatch",      "does not match tasks.json entry"),
]

VALID_CASES = [
    "fixture-incomplete-tasks-valid",
    "fixture-wrong-state-valid",
    "fixture-missing-tasks-entry-valid",
    "fixture-phase-mismatch-valid",
]
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_negative_fixtures.py -v
```
Expected: All 8 cases PASS.

- [ ] **Step 7: Commit**

```bash
git add tests/test_negative_fixtures.py \
        tests/fixtures/fixture-wrong-state \
        tests/fixtures/fixture-wrong-state-valid \
        tests/fixtures/fixture-missing-tasks-entry \
        tests/fixtures/fixture-missing-tasks-entry-valid \
        tests/fixtures/fixture-phase-mismatch \
        tests/fixtures/fixture-phase-mismatch-valid
git commit -m "test(negative-fixtures): state/tasks consistency fixtures (#47)"
```

---

## Task T3: Traceability internal fixtures

**Fixtures:** `fixture-no-test-mapping`, `fixture-orphan-spec-ac`, `fixture-duplicate-spec-ac` (+ valid counterparts)

**Interfaces:**
- Consumes: helpers from T1
- Produces: 3 more negative + 3 more valid parametrize cases

All three fixtures use:
- `.sdd/state.json`: `{"tier": 2, "phase": "implement", "feature": "my-feature"}`
- `.sdd/tasks.json`: `[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]`

- [ ] **Step 1: Create `fixture-no-test-mapping/`**

`specs/my-feature/spec.md`: base spec.md

`specs/my-feature/tasks.md`:
```markdown
# Tasks: my-feature
- [x] T1: first task. AC: SAC-1
- [x] T2: second task. AC: SAC-2
```

`specs/my-feature/traceability.json`:
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
      "test": "tests/test_nonexistent_file.py::test_something",
      "status": "in-scope"
    },
    {
      "issue_ac": "99-AC2",
      "spec_ac": "SAC-2",
      "task": "T2",
      "test": "tests/test_my_feature.py::test_something_else",
      "status": "in-scope"
    }
  ]
}
```

`tests/test_my_feature.py`: base test file (only `test_something_else` — `test_nonexistent_file.py` deliberately missing)

`specs/my-feature/issue-snapshot.json`: base issue-snapshot.json
`specs/my-feature/evidence.json`: base evidence.json (SHA placeholder)

`README.md`:
```markdown
## fixture-no-test-mapping

**再現パターン:** `traceability.json` の `test` フィールドが存在しないテストファイルを参照している。

**対応チェック:** Check 6 — `check_traceability_internal`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-no-test-mapping
# → exit 1, stderr に "test file not found" が含まれる
```
```

- [ ] **Step 2: Create `fixture-orphan-spec-ac/`**

`specs/my-feature/spec.md`:
```markdown
# Spec: my-feature

## Acceptance Criteria

- SAC-1: first criterion works
```
(SAC-2 is intentionally absent — traceability references it but spec.md does not define it)

`specs/my-feature/tasks.md`:
```markdown
# Tasks: my-feature
- [x] T1: first task. AC: SAC-1
- [x] T2: second task. AC: SAC-2
```

`specs/my-feature/traceability.json`: base traceability.json (references SAC-2 which is not in spec.md)

`tests/test_my_feature.py`: base test file

`specs/my-feature/issue-snapshot.json`: base issue-snapshot.json
`specs/my-feature/evidence.json`: base evidence.json (SHA placeholder)

`README.md`:
```markdown
## fixture-orphan-spec-ac

**再現パターン:** `traceability.json` の `spec_ac` が `spec.md` に定義されていない。

**対応チェック:** Check 6 — `check_traceability_internal`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-orphan-spec-ac
# → exit 1, stderr に "not found in spec.md" が含まれる
```
```

- [ ] **Step 3: Create `fixture-duplicate-spec-ac/`**

`specs/my-feature/spec.md`: base spec.md

`specs/my-feature/tasks.md`:
```markdown
# Tasks: my-feature
- [x] T1: first task. AC: SAC-1
- [x] T2: second task. AC: SAC-1
```
(T2 intentionally uses SAC-1 again)

`specs/my-feature/traceability.json`:
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
    },
    {
      "issue_ac": "99-AC2",
      "spec_ac": "SAC-1",
      "task": "T2",
      "test": "tests/test_my_feature.py::test_something_else",
      "status": "in-scope"
    }
  ]
}
```

`tests/test_my_feature.py`: base test file
`specs/my-feature/issue-snapshot.json`: base issue-snapshot.json
`specs/my-feature/evidence.json`: base evidence.json (SHA placeholder)

`README.md`:
```markdown
## fixture-duplicate-spec-ac

**再現パターン:** `traceability.json` の2エントリが同一の `spec_ac` ID を持つ。

**対応チェック:** Check 6 — `check_traceability_internal`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-duplicate-spec-ac
# → exit 1, stderr に "duplicate spec_ac" が含まれる
```
```

- [ ] **Step 4: Create valid counterparts**

All three valid fixtures use:
- state.json: `{"tier": 2, "phase": "implement", "feature": "my-feature"}`
- tasks.json: `[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]`
- Full spec.md (both SAC-1 and SAC-2 defined)
- traceability.json: base (no duplicates, SAC-1 and SAC-2 distinct, test file exists)
- issue-snapshot.json: base
- evidence.json: base (SHA placeholder)
- tests/test_my_feature.py: base

- [ ] **Step 5: Update `NEGATIVE_CASES` and `VALID_CASES`**

```python
NEGATIVE_CASES = [
    ("fixture-incomplete-tasks",    "unchecked item"),
    ("fixture-wrong-state",         "no matching entry"),
    ("fixture-missing-tasks-entry", "no entry for feature"),
    ("fixture-phase-mismatch",      "does not match tasks.json entry"),
    ("fixture-no-test-mapping",     "test file not found"),
    ("fixture-orphan-spec-ac",      "not found in spec.md"),
    ("fixture-duplicate-spec-ac",   "duplicate spec_ac"),
]

VALID_CASES = [
    "fixture-incomplete-tasks-valid",
    "fixture-wrong-state-valid",
    "fixture-missing-tasks-entry-valid",
    "fixture-phase-mismatch-valid",
    "fixture-no-test-mapping-valid",
    "fixture-orphan-spec-ac-valid",
    "fixture-duplicate-spec-ac-valid",
]
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_negative_fixtures.py -v
```
Expected: All 14 cases PASS.

- [ ] **Step 7: Commit**

```bash
git add tests/test_negative_fixtures.py \
        tests/fixtures/fixture-no-test-mapping \
        tests/fixtures/fixture-no-test-mapping-valid \
        tests/fixtures/fixture-orphan-spec-ac \
        tests/fixtures/fixture-orphan-spec-ac-valid \
        tests/fixtures/fixture-duplicate-spec-ac \
        tests/fixtures/fixture-duplicate-spec-ac-valid
git commit -m "test(negative-fixtures): traceability internal check fixtures (#47)"
```

---

## Task T4: Scope-out fixture

**Fixture:** `fixture-scope-out-no-followup` (+ valid counterpart)

- [ ] **Step 1: Create `fixture-scope-out-no-followup/`**

`.sdd/state.json`: `{"tier": 2, "phase": "implement", "feature": "my-feature"}`
`.sdd/tasks.json`: `[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]`

`specs/my-feature/spec.md`: base spec.md

`specs/my-feature/traceability.json`:
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
    },
    {
      "issue_ac": "99-AC2",
      "spec_ac": null,
      "task": null,
      "test": null,
      "status": "out-of-scope",
      "reason": "not in MVP",
      "followup_issue": "not-a-url"
    }
  ]
}
```
(Note: `followup_issue` is not an HTTP(S) URL — triggers Check 7)

`specs/my-feature/tasks.md`:
```markdown
# Tasks: my-feature
- [x] T1: first task. AC: SAC-1
```

`tests/test_my_feature.py`:
```python
def test_something():
    pass
```

`specs/my-feature/issue-snapshot.json`: base issue-snapshot.json
`specs/my-feature/evidence.json`: base evidence.json (SHA placeholder)

`README.md`:
```markdown
## fixture-scope-out-no-followup

**再現パターン:** `out-of-scope` エントリの `followup_issue` が HTTP(S) URL ではない。

**対応チェック:** Check 7 — `check_scope_out`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-scope-out-no-followup
# → exit 1, stderr に "missing HTTP(S) followup_issue" が含まれる
```
```

- [ ] **Step 2: Create `fixture-scope-out-no-followup-valid/`**

Same structure but traceability.json has:
```json
{
  "issue_ac": "99-AC2",
  "spec_ac": null,
  "task": null,
  "test": null,
  "status": "out-of-scope",
  "reason": "not in MVP",
  "followup_issue": "https://github.com/owner/repo/issues/100"
}
```

- [ ] **Step 3: Update NEGATIVE_CASES and VALID_CASES**

```python
NEGATIVE_CASES = [
    # ... previous entries ...
    ("fixture-scope-out-no-followup", "missing HTTP(S) followup_issue"),
]

VALID_CASES = [
    # ... previous entries ...
    "fixture-scope-out-no-followup-valid",
]
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_negative_fixtures.py -v
```
Expected: All 16 cases PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_negative_fixtures.py \
        tests/fixtures/fixture-scope-out-no-followup \
        tests/fixtures/fixture-scope-out-no-followup-valid
git commit -m "test(negative-fixtures): scope-out fixture (#47)"
```

---

## Task T5: Snapshot fixtures

**Fixtures:** `fixture-weakened-ac`, `fixture-stale-snapshot-hash`, `fixture-untracked-issue-ac` (+ valid counterparts)

All three use:
- `.sdd/state.json`: `{"tier": 2, "phase": "implement", "feature": "my-feature"}`
- `.sdd/tasks.json`: `[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]`
- Base spec.md, tasks.md (all complete), traceability.json (2 in-scope entries with existing test file), evidence.json (SHA placeholder)

- [ ] **Step 1: Create `fixture-weakened-ac/`**

`specs/my-feature/issue-snapshot.json`:
```json
{
  "issue": 99,
  "url": "https://github.com/owner/repo/issues/99",
  "fetched_at": "2026-09-29T00:00:00Z",
  "raw_body": "## 受入条件\n\n- [ ] first criterion works\n- [ ] second criterion works\n- [ ] third criterion works (dropped)\n",
  "body_hash": "COMPUTE_BELOW",
  "stable_acs": [
    {"id": "99-AC1", "text": "first criterion works"},
    {"id": "99-AC2", "text": "second criterion works"},
    {"id": "99-AC3", "text": "third criterion works (dropped)"}
  ]
}
```

Compute body_hash for this raw_body:
```bash
python3 -c "
import hashlib
raw = '## 受入条件\n\n- [ ] first criterion works\n- [ ] second criterion works\n- [ ] third criterion works (dropped)\n'
print(hashlib.sha256(raw.encode('utf-8')).hexdigest())
"
```
Result: `fcc27758c4e82f3deeb5bb4b41717a681d41e3ce9933c3cdbaa28d0b4e9af20f`

The traceability.json only has entries for 99-AC1 and 99-AC2. 99-AC3 is in the snapshot but NOT in traceability → triggers "snapshot AC not tracked in traceability.json".

`README.md`:
```markdown
## fixture-weakened-ac

**再現パターン:** `issue-snapshot.json` の `stable_acs` に存在する AC が `traceability.json` に追跡されていない（scope-out entry もない）。

**対応チェック:** Check 8 — `check_issue_snapshot`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-weakened-ac
# → exit 1, stderr に "snapshot AC not tracked in traceability" が含まれる
```
```

- [ ] **Step 2: Create `fixture-stale-snapshot-hash/`**

`specs/my-feature/issue-snapshot.json`:
```json
{
  "issue": 99,
  "url": "https://github.com/owner/repo/issues/99",
  "fetched_at": "2026-09-29T00:00:00Z",
  "raw_body": "## 受入条件\n\n- [ ] first criterion works — EDITED AFTER SNAPSHOT\n- [ ] second criterion works\n",
  "body_hash": "0e9cc93e6d0e5c2c0d87a643b36e8cd22fcad4f1a9b78d01b0dbb8dc37c7b4a4",
  "stable_acs": [
    {"id": "99-AC1", "text": "first criterion works"},
    {"id": "99-AC2", "text": "second criterion works"}
  ]
}
```
(raw_body was edited after capture but body_hash is from the original text → hash mismatch)

`README.md`:
```markdown
## fixture-stale-snapshot-hash

**再現パターン:** `raw_body` を改変したが `body_hash` が更新されていない（SHA-256 不一致）。

**対応チェック:** Check 8 — `check_issue_snapshot`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-stale-snapshot-hash
# → exit 1, stderr に "body_hash does not match" が含まれる
```
```

- [ ] **Step 3: Create `fixture-untracked-issue-ac/`**

`specs/my-feature/traceability.json`:
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
    },
    {
      "issue_ac": "99-AC2",
      "spec_ac": "SAC-2",
      "task": "T2",
      "test": "tests/test_my_feature.py::test_something_else",
      "status": "in-scope"
    },
    {
      "issue_ac": "99-AC99",
      "spec_ac": null,
      "task": null,
      "test": null,
      "status": "out-of-scope",
      "reason": "phantom AC not in snapshot",
      "followup_issue": "https://github.com/owner/repo/issues/999"
    }
  ]
}
```
(99-AC99 exists in traceability but NOT in issue-snapshot.json → triggers "traceability AC not in snapshot")

`specs/my-feature/issue-snapshot.json`: base issue-snapshot.json (only has 99-AC1, 99-AC2)

`README.md`:
```markdown
## fixture-untracked-issue-ac

**再現パターン:** `traceability.json` の `issue_ac` が `issue-snapshot.json` の `stable_acs` に存在しない。

**対応チェック:** Check 8 — `check_issue_snapshot`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-untracked-issue-ac
# → exit 1, stderr に "traceability AC not in snapshot" が含まれる
```
```

- [ ] **Step 4: Create valid counterparts**

All three valid fixtures use:
- Base snapshot (99-AC1, 99-AC2 only, correct body_hash)
- Base traceability (99-AC1, 99-AC2 only)
- Base spec.md, tasks.md, evidence.json (SHA placeholder)
- tests/test_my_feature.py base

- [ ] **Step 5: Update NEGATIVE_CASES and VALID_CASES**

```python
NEGATIVE_CASES = [
    # ... previous entries ...
    ("fixture-weakened-ac",         "snapshot AC not tracked in traceability"),
    ("fixture-stale-snapshot-hash", "body_hash does not match"),
    ("fixture-untracked-issue-ac",  "traceability AC not in snapshot"),
]

VALID_CASES = [
    # ... previous entries ...
    "fixture-weakened-ac-valid",
    "fixture-stale-snapshot-hash-valid",
    "fixture-untracked-issue-ac-valid",
]
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_negative_fixtures.py -v
```
Expected: All 22 cases PASS.

- [ ] **Step 7: Commit**

```bash
git add tests/test_negative_fixtures.py \
        tests/fixtures/fixture-weakened-ac \
        tests/fixtures/fixture-weakened-ac-valid \
        tests/fixtures/fixture-stale-snapshot-hash \
        tests/fixtures/fixture-stale-snapshot-hash-valid \
        tests/fixtures/fixture-untracked-issue-ac \
        tests/fixtures/fixture-untracked-issue-ac-valid
git commit -m "test(negative-fixtures): snapshot check fixtures (#47)"
```

---

## Task T6: Evidence fixtures

**Fixtures:** `fixture-invalid-evidence-commit`, `fixture-non-test-count`, `fixture-missing-test-count` (+ valid counterparts)

All three use:
- `.sdd/state.json`: `{"tier": 2, "phase": "implement", "feature": "my-feature"}`
- `.sdd/tasks.json`: `[{"id": "my-feature", "phase": "implement", "status": "in_progress", "handoff": null, "blocked_reason": null}]`
- Base spec.md, tasks.md, traceability.json, issue-snapshot.json, test file

- [ ] **Step 1: Create `fixture-invalid-evidence-commit/`**

`specs/my-feature/evidence.json`:
```json
{
  "feature": "my-feature",
  "commit_sha": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
  "entries": [
    {
      "command_type": "test",
      "command": "pytest tests/test_my_feature.py",
      "result": "2 passed",
      "test_count": 2
    }
  ]
}
```

`README.md`:
```markdown
## fixture-invalid-evidence-commit

**再現パターン:** `evidence.json` の `commit_sha` が git リポジトリに存在しない SHA。

**対応チェック:** Check 9 — `check_evidence`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-invalid-evidence-commit
# → exit 1, stderr に "commit_sha not found in git repository" が含まれる
```
```

- [ ] **Step 2: Create `fixture-non-test-count/`**

`specs/my-feature/evidence.json`:
```json
{
  "feature": "my-feature",
  "commit_sha": "0000000000000000000000000000000000000000",
  "entries": [
    {
      "command_type": "lint",
      "command": "git diff --check",
      "result": "no output",
      "test_count": 5
    }
  ]
}
```
(lint entry has non-null `test_count` → schema violation: lint must have `test_count: null`)

`README.md`:
```markdown
## fixture-non-test-count

**再現パターン:** `lint` コマンドの `test_count` が `null` ではなく整数値になっている（スキーマ違反）。

**対応チェック:** Check 9 — `check_evidence` (schema validation)

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-non-test-count
# → exit 1, stderr に "test_count" が含まれる
```
```

- [ ] **Step 3: Create `fixture-missing-test-count/`**

`specs/my-feature/evidence.json`:
```json
{
  "feature": "my-feature",
  "commit_sha": "0000000000000000000000000000000000000000",
  "entries": [
    {
      "command_type": "test",
      "command": "pytest tests/test_my_feature.py",
      "result": "2 passed",
      "test_count": null
    }
  ]
}
```
(test entry has `test_count: null` → schema violation: test must have integer `test_count`)

`README.md`:
```markdown
## fixture-missing-test-count

**再現パターン:** `test` コマンドの `test_count` が `null`（スキーマ違反: test は整数を必須とする）。

**対応チェック:** Check 9 — `check_evidence` (schema validation)

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-missing-test-count
# → exit 1, stderr に "test_count" が含まれる
```
```

- [ ] **Step 4: Create valid counterparts**

`fixture-invalid-evidence-commit-valid/`: base evidence.json (placeholder SHA — injected at test time)
`fixture-non-test-count-valid/`: lint entry with `test_count: null` and a valid test entry with integer test_count
`fixture-missing-test-count-valid/`: test entry with integer `test_count: 2`

For `fixture-non-test-count-valid/` evidence.json:
```json
{
  "feature": "my-feature",
  "commit_sha": "0000000000000000000000000000000000000000",
  "entries": [
    {
      "command_type": "test",
      "command": "pytest tests/test_my_feature.py",
      "result": "2 passed",
      "test_count": 2
    },
    {
      "command_type": "lint",
      "command": "git diff --check",
      "result": "no output",
      "test_count": null
    }
  ]
}
```

For `fixture-missing-test-count-valid/` evidence.json:
```json
{
  "feature": "my-feature",
  "commit_sha": "0000000000000000000000000000000000000000",
  "entries": [
    {
      "command_type": "test",
      "command": "pytest tests/test_my_feature.py",
      "result": "2 passed",
      "test_count": 2
    }
  ]
}
```

- [ ] **Step 5: Update NEGATIVE_CASES and VALID_CASES (final)**

```python
NEGATIVE_CASES = [
    ("fixture-incomplete-tasks",           "unchecked item"),
    ("fixture-wrong-state",                "no matching entry"),
    ("fixture-missing-tasks-entry",        "no entry for feature"),
    ("fixture-phase-mismatch",             "does not match tasks.json entry"),
    ("fixture-no-test-mapping",            "test file not found"),
    ("fixture-orphan-spec-ac",             "not found in spec.md"),
    ("fixture-duplicate-spec-ac",          "duplicate spec_ac"),
    ("fixture-scope-out-no-followup",      "missing HTTP(S) followup_issue"),
    ("fixture-weakened-ac",               "snapshot AC not tracked in traceability"),
    ("fixture-stale-snapshot-hash",        "body_hash does not match"),
    ("fixture-untracked-issue-ac",         "traceability AC not in snapshot"),
    ("fixture-invalid-evidence-commit",    "commit_sha not found in git repository"),
    ("fixture-non-test-count",            "test_count"),
    ("fixture-missing-test-count",        "test_count"),
]

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
```

- [ ] **Step 6: Run full test suite**

```bash
pytest tests/test_negative_fixtures.py -v
```
Expected: All 28 cases PASS.

Also run the full suite to check for regressions:
```bash
pytest tests/ -v --tb=short
```
Expected: All existing tests continue to PASS.

- [ ] **Step 7: Commit**

```bash
git add tests/test_negative_fixtures.py \
        tests/fixtures/fixture-invalid-evidence-commit \
        tests/fixtures/fixture-invalid-evidence-commit-valid \
        tests/fixtures/fixture-non-test-count \
        tests/fixtures/fixture-non-test-count-valid \
        tests/fixtures/fixture-missing-test-count \
        tests/fixtures/fixture-missing-test-count-valid
git commit -m "test(negative-fixtures): evidence check fixtures (#47)"
```

---

## Task T7: SDD artifacts, traceability freeze, state update

**Files:**
- Create: `specs/negative-tests/spec.md`
- Create: `specs/negative-tests/plan.md`
- Create: `specs/negative-tests/tasks.md`
- Create: `specs/negative-tests/traceability.json`
- Create: `specs/negative-tests/issue-snapshot.json`
- Create: `specs/negative-tests/handoff.md`
- Update: `.sdd/state.json`
- Update: `.sdd/tasks.json`

Note: This task is handled by the **design agent (current session)** as the freeze step, not by the implementation agent.

- [ ] **Step 1: Verify all 28 tests pass + CI green**

```bash
pytest tests/ -v --tb=short 2>&1 | tail -20
```
Expected: no failures.

- [ ] **Step 2: Update `.sdd/state.json`** (post-implementation, pre-verify)

```json
{"tier": 2, "phase": "verify", "feature": "negative-tests"}
```

- [ ] **Step 3: Update `.sdd/tasks.json`** — set `negative-tests` entry to `status: completed`

```json
[
  ...,
  {"id": "negative-tests", "phase": "verify", "status": "completed", "handoff": "specs/negative-tests/handoff.md", "blocked_reason": null}
]
```

- [ ] **Step 4: Commit all SDD artifacts**

```bash
git add specs/negative-tests/ .sdd/state.json .sdd/tasks.json
git commit -m "docs(negative-tests): freeze SDD artifacts (#47)"
```

- [ ] **Step 5: Create PR**

```bash
gh pr create --title "test: negative fixtures for SDD validator (#47)" \
  --body "closes #47

## Summary
- 14 negative fixture directories under tests/fixtures/fixture-*/
- 14 valid counterparts (fixture-*-valid/)
- tests/test_negative_fixtures.py with 28 parametrized RED/GREEN cases
- README.md in each negative fixture documenting the pattern

## Test plan
- [ ] pytest tests/test_negative_fixtures.py all pass
- [ ] pytest tests/ (full suite) no regressions
- [ ] CI green"
```
