# Handoff: 96-ai-merge

## Your scope

Implementation phase only. Do not touch `spec.md`, `plan.md`, `traceability.json`, or the verify phase.
In `tasks.md` you may only check boxes (`- [ ]` → `- [x]`).
If the spec needs changes, stop and report to the orchestrating agent.

## Done when

- [ ] All tasks in `specs/96-ai-merge/tasks.md` are complete (T1–T4 and the verification list checked)
- [ ] Every SAC is satisfied by the diff; write no new tests (spec D6) and keep the existing suite green
- [ ] Test suite passes (`uv run --no-project --with pytest --with jsonschema python -m pytest tests -q`)

## Reference files

- spec:  `specs/96-ai-merge/spec.md` (the new flow, merge conditions, cleanup and report, decisions D1–D6)
- plan:  `specs/96-ai-merge/plan.md` (exact passages to change per file)
- tasks: `specs/96-ai-merge/tasks.md`
- Issue: #96

## If the spec is ambiguous or insufficient

1. Stop immediately.
2. Report the reason to the orchestrating agent.
3. Do not redesign. The orchestrating agent resolves it through spec review or escalates
   (Escalation conditions in `orchestration/rules/orchestration.md`).

## Notes

- This repository is the guide itself: rules are at `rules/` and `orchestration/rules/` (not `vendor/`).
- Do not edit past version sections of `docs/migration.md`, `rules/repo-agent-routing.md`, past `specs/` or `_dev/`.
- `rules/` and the AGENTS examples are English, terse, imperative; `docs/`, `templates/pr-body.md` and `README.md` are Japanese in the surrounding style. Keep edits minimal outside the passages named in plan.md.
- `sdd-validate.py --pr` fails only on the missing `evidence.json` until verify; that is expected.
- Commit per task with messages like `docs(96-ai-merge): ...`, each ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push, open a PR, merge, or run `sdd-board.sh`.
