# Fixture roots for `sdd-validate.sh`

Run any fixture with:

```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/<fixture-name>
```

Fixtures:

- `valid-active`: shared Tier 2 happy-path tree with valid `traceability.json`, `issue-snapshot.json`, and `evidence.json`.
- `valid-done`: done-reset tree; feature checks are skipped.
- `invalid-state-mismatch`: `.sdd/state.json` feature does not match `.sdd/tasks.json`.
- `invalid-tasks-incomplete`: verify-phase `tasks.md` still contains an unchecked task.
- `invalid-traceability`: `traceability.json` includes duplicate `spec_ac` entries and missing test files.
- `invalid-snapshot-hash-mismatch`: `issue-snapshot.json` has a `body_hash` that does not match `raw_body`.
- `invalid-evidence-bad-commit`: `evidence.json` references a `commit_sha` that does not exist in the repository.
