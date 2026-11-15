# Handoff: 95-no-content-tests

## Your scope

Implementation phase only. Do not touch `spec.md`, `plan.md`, `traceability.json`, or the verify phase.
In `tasks.md` you may only check boxes (`- [ ]` → `- [x]`).
If the spec needs changes, stop and report to the orchestrating agent.

## Done when

- [ ] All tasks in `specs/95-no-content-tests/tasks.md` are complete (T1–T6 and the verification list checked)
- [ ] SAC-3 has passing tests; the other SACs are satisfied by the diff (do not write tests for them)
- [ ] Test suite passes (`uv run --no-project --with pytest --with jsonschema python -m pytest tests -q`)
- [ ] `uv run -q --no-project --with jsonschema python integration/ci/sdd-validate.py --root . --branch t2/95-no-content-tests` passes after T1

## Reference files

- spec:  `specs/95-no-content-tests/spec.md` (rules content, decisions D1–D5, the delete/keep list of tests)
- plan:  `specs/95-no-content-tests/plan.md` (exact passages to change per file, new tests)
- tasks: `specs/95-no-content-tests/tasks.md`
- Issue: #95

## If the spec is ambiguous or insufficient

1. Stop immediately.
2. Report the reason to the orchestrating agent.
3. Do not redesign. The orchestrating agent resolves it through spec review or escalates
   (Escalation conditions in `orchestration/rules/orchestration.md`).

## Notes

- This repository is the guide itself: rules are at `rules/` and `orchestration/rules/` (not `vendor/`).
- Never add a test that only re-checks written content — that is the subject of this feature.
- Do not change anything about "AI never merges" (Issue #96).
- `rules/` English, terse, imperative; `docs/` and `templates/` Japanese in the surrounding style. Keep edits minimal outside the passages named in plan.md.
- Commit per task with messages like `feat(95-no-content-tests): ...` / `docs(95-no-content-tests): ...` / `test(95-no-content-tests): ...`, each ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push, open a PR, or run `sdd-board.sh`.
