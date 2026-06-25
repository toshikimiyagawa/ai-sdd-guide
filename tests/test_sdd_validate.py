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
