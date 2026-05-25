# SDD Workflow Rules (agent)

## Step 0 — classify Tier (always first)
- Tier 0 — trivial (typo, comment, docs-only, formatting): implement directly. No artifacts.
- Tier 1 — small (localized bugfix, small change): lightweight spec (intent + acceptance criteria) + tests. Skip plan/tasks.
- Tier 2 — medium/large (new feature, multi-file, design change, public API): full flow below.
- When unsure, pick the higher Tier.
- Record the Tier in `.sdd/state.json` and label the PR `sdd:tier-{0,1,2}`.

## Design phases (Claude only)
1. Brainstorm — clarify intent with the human (superpowers). Output: agreed intent.
2. Spec — write `specs/<feature>/spec.md`. Acceptance criteria as checkable statements. Get human approval.
3. Plan — write `plan.md`: approach, affected files, tradeoffs, alternatives considered. (Tier 2)
4. Tasks — write `tasks.md`: ordered concrete steps with file paths + the test proving each acceptance criterion. (Tier 2)
5. Freeze — set `.sdd/state.json` `phase=implement`. This is the handoff gate to other agents.

Delegate exploration/drafting to subagents to protect context. See `subagents.md`.

## Implementation phase (any agent)
- Read `specs/<feature>/`. Implement exactly the frozen tasks — no more, no less.
- Map every acceptance criterion to a passing test.
- If the spec is wrong, ambiguous, or insufficient: STOP and escalate. Do not redesign.

## Verify phase (Claude)
- Run tests. Spawn the `sdd-reviewer` subagent to check conformance to the frozen spec.
- CI is authoritative: it independently re-checks spec presence + tests.

## Tier exemptions
- Tier 0: hooks and CI skip the spec requirement.
- Tier 1: lightweight spec required; plan/tasks skipped.
- Tier 2: nothing skipped.
- Exemptions must be declared in `.sdd/state.json` + PR label so hooks/CI can verify them.
