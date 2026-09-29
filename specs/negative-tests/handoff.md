# Handoff: negative-tests

## Your scope

Implementation phase only. Do not touch `spec.md`, `plan.md`, or the verify phase.
If the spec needs changes, stop and escalate to a human.

## Done when

- [x] All tasks in `specs/negative-tests/tasks.md` are complete
- [x] Every acceptance criterion in `specs/negative-tests/spec.md` has a passing test
- [x] Test suite passes (`pytest tests/ -v` — all green including existing tests)

## Reference files

- spec:       `specs/negative-tests/spec.md`
- plan:       `specs/negative-tests/plan.md`
- tasks:      `specs/negative-tests/tasks.md`
- detail plan: `_dev/plans/2026-09-29-negative-fixtures.md`

## Key facts

- Fixture base dir: `tests/fixtures/`
- Naming: `fixture-<name>/` (negative), `fixture-<name>-valid/` (valid)
- Test file to create: `tests/test_negative_fixtures.py` — do NOT modify `test_sdd_validate.py`
- Valid fixtures with `evidence.json`: include placeholder SHA `"0000000000000000000000000000000000000000"`; the `_prepare_valid_fixture` helper injects the real HEAD SHA at test time
- Shared fixture feature slug: `my-feature`; shared issue number: `99`
- body_hash for base issue-snapshot (raw_body = 2 AC items): `49f9de3f0073cf45c66066aae898543b31bb5b7b32c20e33531b4e90a3ba7541`

## If the spec is ambiguous or insufficient

1. Stop immediately.
2. Set `.sdd/tasks.json` status to `"blocked"`.
3. Fill in `blocked_reason`.
4. Wait for a human to escalate to Claude before resuming.
