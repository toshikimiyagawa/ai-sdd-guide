# Tasks: evidence-validation

- [ ] T1: Add `orchestration/schema/evidence.schema.json` with strict `test_count` rules and schema tests.
- [ ] T2: Extend `integration/ci/sdd-validate.py` with `check_evidence` and commit SHA existence checks.
- [ ] T3: Add validator tests for valid evidence, bad commit SHA, and fail-closed missing/broken evidence.
- [ ] T4: Create this feature's `specs/evidence-validation/evidence.json` during verify and run the full validation suite.
