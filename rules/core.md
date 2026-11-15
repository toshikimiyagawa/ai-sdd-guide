# SDD Core Rules (agent)

Canonical, always-loaded rules. Terse + imperative. Rationale lives in `docs/` (Japanese).

## Scope
- DESIGN phases (spec, plan, tasks, verify) — superpowers required, any agent. Use superpowers + subagents + hooks.
- IMPLEMENTATION phase — any agent. Follow `specs/<feature>/` as the contract. Do not deviate.

## Always
- Classify every task into a Tier before touching code. See `workflow.md`.
- Tier 1/2: no source edits until the spec is frozen (`specs/<feature>/freeze.json`; Tier 2 also needs `plan.md` and `tasks.md`).
- Every acceptance criterion names how it is verified: a passing test, or the diff. Changes to behavior (code, scripts, hooks, schemas) need tests for Tier 1+.
- Verify by the diff, not by a test, any criterion that only states that docs, rules, config, data, templates or wording were written, changed or removed. The reviewer cites the diff lines.
- Never write a test that only re-checks written content: that a doc, rule, config, data file, template or workflow contains (or lacks) a given line, value, phrase, heading or key (order and counts included); that only given lines changed since a fixed commit; or that source code contains a given expression. It guards nothing — the next intended change just breaks it.
- Write tests for behavior: run code, scripts, hooks or CLIs with inputs and check output, exit codes and files; validate data against schemas; mechanical checks that apply to every file of a kind; consistency between artifacts that must agree.
- Every piece of work (Tier 0 included) has an Issue. Name the branch `t<Tier>/<Issue番号>-<名前>`; the Tier, feature (`<Issue番号>-<名前>`) and phase are derived from the branch name and the files under `specs/<feature>/` — there is no state file to maintain. Hooks and CI use the same derivation.
- Human touchpoints are limited to the initial question and escalation; afterwards the human checks the result. Run every other step autonomously, through merging the PR and cleaning up (`## Merge conditions`, `## Cleanup and report` in `orchestration/rules/orchestration.md`).
- When stuck (spec wrong or insufficient, blocked), resolve it through spec review or escalate only under `## Escalation conditions` (`orchestration/rules/orchestration.md`). Never silently redesign during implementation.
- Tier 2: every Issue AC must appear in `specs/<feature>/traceability.json` before freeze.
  If any Issue AC is untracked, STOP — do not freeze and do not implement.
- Freeze targets: Tier 2 freezes `spec.md`, `plan.md`, `tasks.md`, `traceability.json`; Tier 1 freezes `spec.md` only.
- Frozen artifacts (Tier 2: `spec.md`, `plan.md`, `tasks.md`, `traceability.json`; Tier 1: `spec.md`) are immutable after freeze.
  The only permitted post-freeze edit to `tasks.md` is checkbox state ([ ] → [x]).
  Any other post-freeze change (including `traceability.json`) requires explicit unfreeze: a new spec review `APPROVE` (human approval instead if the change falls under Escalation conditions 1 or 2), then re-run `vendor/ai-sdd-guide/orchestration/tools/sdd-freeze.sh` to recreate `freeze.json`.

## Never
- Never edit source code during spec/plan/tasks phases (only specs/docs).
- Never expand scope beyond the approved tasks. New ideas become a new spec.
- Never disable or bypass SDD hooks or CI to make a change pass.
- Never freeze a spec that has no acceptance criteria.
- Never modify files under `specs/` to fit an implementation.

## The contract for other agents
`specs/<feature>/` is the only thing an implementation agent receives. It must be self-contained
enough to implement with zero design-conversation context.
- `spec.md`  — intent + acceptance criteria
- `plan.md`  — approach + affected files + tradeoffs (Tier 2)
- `tasks.md` — ordered, concrete, tool-agnostic steps + how each criterion is verified (test or diff) (Tier 2)
