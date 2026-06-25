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
