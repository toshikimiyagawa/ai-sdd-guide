"""Tests for issue-snapshot.schema.json."""
import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "orchestration" / "schema" / "issue-snapshot.schema.json"

RAW_BODY = "## 受入条件\n\n- [ ] first criterion\n- [ ] second criterion\n"
VALID_SNAPSHOT = {
    "issue": 53,
    "url": "https://github.com/owner/repo/issues/53",
    "fetched_at": "2026-06-26T13:50:53Z",
    "raw_body": RAW_BODY,
    "body_hash": hashlib.sha256(RAW_BODY.encode("utf-8")).hexdigest(),
    "stable_acs": [
        {"id": "53-AC1", "text": "first criterion"},
        {"id": "53-AC2", "text": "second criterion"},
    ],
}


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def validate(instance: dict, schema: dict) -> None:
    jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())


def test_valid_issue_snapshot_passes_schema(schema):
    validate(VALID_SNAPSHOT, schema)


def test_invalid_stable_ac_id_fails_schema(schema):
    instance = copy.deepcopy(VALID_SNAPSHOT)
    instance["stable_acs"][0]["id"] = "53-ACX"
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_missing_required_field_fails_schema(schema):
    instance = copy.deepcopy(VALID_SNAPSHOT)
    del instance["raw_body"]
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_additional_properties_fail_schema(schema):
    instance = copy.deepcopy(VALID_SNAPSHOT)
    instance["stable_acs"][0]["extra"] = "not allowed"
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)
