# Plan: Evidence Validation

## Goal

Implement Issue #54 by adding verification evidence schema validation and Git
commit existence checks to the SDD validator.

## Constraints

- Preserve the exact field names from Issue #54.
- Do not add an evidence generation CLI in this feature.
- Do not treat lint, build, compile, syntax, or other commands as tests.
- Keep validation fail-closed for missing, malformed, or uncheckable evidence.
- Keep implementation scoped to evidence schema and validator checks.

## Implementation Steps

1. Add `orchestration/schema/evidence.schema.json`.
   - Require `feature`, `commit_sha`, and `entries`.
   - Require `command_type`, `command`, `result`, and `test_count` on every entry.
   - Restrict `command_type` to `test`, `lint`, `build`, and `other`.
   - Constrain `commit_sha` to exactly 40 hexadecimal characters.
   - Use JSON Schema conditionals so `test` entries require integer `test_count`
     and non-test entries require `test_count: null`.
   - Reject unknown properties.

2. Add schema tests.
   - Valid evidence passes.
   - Non-test entry with non-null `test_count` fails.
   - Test entry missing `test_count` fails.
   - Invalid `commit_sha` format fails.

3. Extend `integration/ci/sdd-validate.py`.
   - Add `check_evidence(root, feature)`.
   - Load `specs/<feature>/evidence.json`.
   - Validate it against `evidence.schema.json`.
   - Check `commit_sha` with Git.
   - Return validation errors instead of silently skipping missing or broken evidence.
   - Call `check_evidence` for active Tier 2 features.

4. Add validator tests.
   - Valid evidence with an existing commit passes.
   - Non-existent but well-formed commit SHA fails.
   - Missing evidence fails closed.
   - Broken JSON or Git check failure returns non-zero from the validator entrypoint.

5. Verify the feature.
   - Run the full test suite.
   - Generate `specs/evidence-validation/evidence.json` in the verify phase after
     the implementation commit exists.
   - Re-run the validator with the feature active before resetting `.sdd/state.json`.

## Verification

Run:

```sh
PATH=/tmp/ai-sdd-guide-test-venv/bin:$PATH /tmp/ai-sdd-guide-test-venv/bin/pytest -q
PATH=/tmp/ai-sdd-guide-test-venv/bin:$PATH python3 integration/ci/sdd-validate.py
```
