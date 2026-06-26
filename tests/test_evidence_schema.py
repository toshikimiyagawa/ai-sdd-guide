"""Tests for evidence.schema.json."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "orchestration" / "schema" / "evidence.schema.json"

VALID_EVIDENCE = {
    "feature": "evidence-validation",
    "commit_sha": "0123456789abcdef0123456789abcdef01234567",
    "entries": [
        {
            "command_type": "test",
            "command": "pytest -q",
            "result": "114 passed",
            "test_count": 114,
        },
        {
            "command_type": "lint",
            "command": "git diff --check",
            "result": "no output",
            "test_count": None,
        },
    ],
}


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def validate(instance: dict, schema: dict) -> None:
    jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())


def test_valid_evidence_passes_schema(schema):
    validate(VALID_EVIDENCE, schema)


def test_non_test_entry_with_test_count_fails_schema(schema):
    instance = copy.deepcopy(VALID_EVIDENCE)
    instance["entries"][1]["test_count"] = 1
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_test_entry_missing_test_count_fails_schema(schema):
    instance = copy.deepcopy(VALID_EVIDENCE)
    del instance["entries"][0]["test_count"]
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_invalid_commit_sha_fails_schema(schema):
    instance = copy.deepcopy(VALID_EVIDENCE)
    instance["commit_sha"] = "not-a-40-character-hex-sha"
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)
