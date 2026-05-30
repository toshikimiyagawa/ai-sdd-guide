# SDD Workflow Rules (agent)

## Step 0 — classify Tier (always first)
- Tier 0 — trivial (typo, comment, docs-only, formatting): implement directly. No artifacts.
- Tier 1 — small (localized bugfix, small change): lightweight spec (intent + acceptance criteria) + tests. Skip plan/tasks.
- Tier 2 — medium/large (new feature, multi-file, design change, public API): full flow below.
- When unsure, pick the higher Tier.
- Record the Tier in `.sdd/state.json` and label the PR `sdd:tier-{0,1,2}`.

## Design phases (Claude only)
Drive these with superpowers skills (requires the superpowers plugin — Claude only).
Capture each skill's output into the portable `specs/<feature>/` artifacts.

1. Brainstorm — skill `brainstorming`. Clarify intent with the human, explore alternatives. Output: an agreed design.
2. Spec — write `specs/<feature>/spec.md` from the agreed design. Acceptance criteria as checkable statements. Get human approval.
   - If `.sdd/catalog.json` exists: register new catalog entries as `planned` in `docs/design/` (see `catalog/rules/catalog.md`). Update to `confirmed` in the verify phase.
3. Plan & Tasks — skill `writing-plans` (bite-sized ordered steps). Capture into `plan.md` (approach, affected files, tradeoffs, alternatives) and `tasks.md` (concrete steps + the test proving each acceptance criterion). (Tier 2)
4. Freeze — set `.sdd/state.json` `phase=implement`. This is the handoff gate to other agents.

For exploration/parallelism use skills `dispatching-parallel-agents` / `subagent-driven-development`. See `subagents.md`.

## Implementation phase (any agent)
- Read `specs/<feature>/`. Implement exactly the frozen tasks — no more, no less.
- Map every acceptance criterion to a passing test.
- When Claude implements: use skills `executing-plans` + `test-driven-development` (RED-GREEN-REFACTOR) + `systematic-debugging`. Other agents follow `tasks.md` directly.
- If the spec is wrong, ambiguous, or insufficient: STOP and escalate. Do not redesign.

## Verify phase (Claude)
- Skill `verification-before-completion`. Run tests; spawn the `sdd-reviewer` subagent to check conformance to the frozen spec.
- When sdd-reviewer or any code review returns feedback: skill `receiving-code-review`. Evaluate each item against the frozen spec before acting. If feedback conflicts with the frozen spec, STOP and escalate to the human — do not silently redesign. Scope-expanding suggestions become a new spec, not a quiet addition.
- Create the PR. CI が設定されている場合は実行完了を待ち、全チェックが pass かつ mergeable であることを確認してから完了報告する。CI 結果を確認せずに完了を宣言してはならない。
- Optionally `requesting-code-review` / `finishing-a-development-branch`.
- CI is authoritative: it independently re-checks spec presence + tests.

## Tier exemptions
- Tier 0: hooks and CI skip the spec requirement.
- Tier 1: lightweight spec required; plan/tasks skipped.
- Tier 2: nothing skipped.
- Exemptions must be declared in `.sdd/state.json` + PR label so hooks/CI can verify them.
