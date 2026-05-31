# SDD Core Rules (agent)

Canonical, always-loaded rules. Terse + imperative. Rationale lives in `docs/` (Japanese).

## Scope
- DESIGN phases (spec, plan, tasks, verify) — superpowers required, any agent. Use superpowers + subagents + hooks.
- IMPLEMENTATION phase — any agent. Follow `specs/<feature>/` as the contract. Do not deviate.

## Always
- Classify every task into a Tier before touching code. See `workflow.md`.
- Tier 2: no source edits until `specs/<feature>/{spec,plan,tasks}.md` exist and are frozen.
- Every acceptance criterion must map to a test. Tests are mandatory for Tier 1+.
- Keep `.sdd/state.json` current (`feature`, `tier`, `phase`). Hooks and CI read it.
- If the spec is wrong or insufficient, STOP and escalate to a human. Never silently redesign during implementation.

## Never
- Never edit source code during spec/plan/tasks phases (only specs/docs).
- Never begin implementation immediately after freezing a spec in the same turn. Wait for an explicit human instruction to start.
- Never treat spec approval ("approved", "LGTM", etc.) as permission to start implementation — these confirm the spec only.
- Never expand scope beyond the approved tasks. New ideas become a new spec.
- Never disable or bypass SDD hooks or CI to make a change pass.
- Never freeze a spec that has no acceptance criteria.
- Never modify files under `specs/` to fit an implementation.

## The contract for other agents
`specs/<feature>/` is the only thing an implementation agent receives. It must be self-contained
enough to implement with zero design-conversation context.
- `spec.md`  — intent + acceptance criteria
- `plan.md`  — approach + affected files + tradeoffs (Tier 2)
- `tasks.md` — ordered, concrete, tool-agnostic steps + the tests that prove each criterion (Tier 2)
