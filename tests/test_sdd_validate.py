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
