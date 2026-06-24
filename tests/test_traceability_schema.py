import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "orchestration" / "schema" / "traceability.schema.json"


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())


VALID_IN_SCOPE = {
    "issue": 50,
    "issue_url": "https://github.com/owner/repo/issues/50",
    "feature": "form-validation",
    "entries": [
        {
            "issue_ac": "50-AC1",
            "spec_ac": "SAC-1",
            "task": "T1",
            "test": "tests/test_form.py::test_validation",
            "status": "in-scope",
        }
    ],
}

VALID_OUT_OF_SCOPE = {
    "issue": 50,
    "issue_url": "https://github.com/owner/repo/issues/50",
    "feature": "form-validation",
    "entries": [
        {
            "issue_ac": "50-AC1",
            "spec_ac": None,
            "task": None,
            "test": None,
            "status": "out-of-scope",
            "reason": "別 feature で扱う",
            "followup_issue": "https://github.com/owner/repo/issues/51",
        }
    ],
}


def validate(instance, schema):
    jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())


def test_valid_in_scope_passes(schema):
    validate(VALID_IN_SCOPE, schema)


def test_valid_out_of_scope_passes(schema):
    validate(VALID_OUT_OF_SCOPE, schema)


def test_valid_deferred_passes(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                **VALID_OUT_OF_SCOPE["entries"][0],
                "status": "deferred",
            }
        ],
    }
    validate(instance, schema)


def test_in_scope_missing_spec_ac_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": "T1",
                "test": "tests/test_form.py::test_validation",
                "status": "in-scope",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_in_scope_missing_task_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": "SAC-1",
                "task": None,
                "test": "tests/test_form.py::test_validation",
                "status": "in-scope",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_in_scope_missing_test_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": "SAC-1",
                "task": "T1",
                "test": None,
                "status": "in-scope",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_out_of_scope_missing_reason_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": None,
                "test": None,
                "status": "out-of-scope",
                "followup_issue": "https://github.com/owner/repo/issues/51",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_out_of_scope_missing_followup_issue_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": None,
                "test": None,
                "status": "out-of-scope",
                "reason": "別 feature で扱う",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_empty_entries_fails(schema):
    instance = {**VALID_IN_SCOPE, "entries": []}
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_invalid_issue_ac_format_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                **VALID_IN_SCOPE["entries"][0],
                "issue_ac": "AC1",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_missing_issue_url_fails(schema):
    instance = {k: v for k, v in VALID_IN_SCOPE.items() if k != "issue_url"}
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


# --- out-of-scope / deferred strict null constraints ---

def test_out_of_scope_nonnull_spec_ac_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": "SAC-1",
                "task": None,
                "test": None,
                "status": "out-of-scope",
                "reason": "別 feature で扱う",
                "followup_issue": "https://github.com/owner/repo/issues/51",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_out_of_scope_nonnull_task_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": "T1",
                "test": None,
                "status": "out-of-scope",
                "reason": "別 feature で扱う",
                "followup_issue": "https://github.com/owner/repo/issues/51",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_out_of_scope_nonnull_test_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": None,
                "test": "tests/test_form.py::test_validation",
                "status": "out-of-scope",
                "reason": "別 feature で扱う",
                "followup_issue": "https://github.com/owner/repo/issues/51",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


# --- reason / followup_issue format constraints ---

def test_empty_reason_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                **VALID_OUT_OF_SCOPE["entries"][0],
                "reason": "",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_mailto_followup_issue_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                **VALID_OUT_OF_SCOPE["entries"][0],
                "followup_issue": "mailto:test@example.com",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_ftp_followup_issue_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                **VALID_OUT_OF_SCOPE["entries"][0],
                "followup_issue": "ftp://example.com/issues/1",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


# --- in-scope task / test format constraints ---

def test_in_scope_invalid_task_format_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                **VALID_IN_SCOPE["entries"][0],
                "task": "anything",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_in_scope_invalid_test_format_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                **VALID_IN_SCOPE["entries"][0],
                "test": "visual check",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


# --- structural / artifact existence tests ---

def test_schema_file_exists():
    assert SCHEMA_PATH.exists(), f"Schema not found: {SCHEMA_PATH}"


def test_example_is_schema_valid(schema):
    example_path = ROOT / "templates" / "traceability.json.example"
    assert example_path.exists(), f"Example not found: {example_path}"
    example = json.loads(example_path.read_text())
    validate(example, schema)


def test_docs_naming_convention():
    docs_path = ROOT / "docs" / "traceability.md"
    assert docs_path.exists(), f"Docs not found: {docs_path}"
    content = docs_path.read_text()
    assert "SAC-" in content, "docs/traceability.md must document SAC-N spec AC ID format"
    assert "AC" in content, "docs/traceability.md must document Issue AC ID format"
