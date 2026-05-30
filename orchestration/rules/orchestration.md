# Orchestration Rules (all agents)

## Scope assignment

Phases and their assigned agents are fixed:

| Phase | Allowed agents | Notes |
|---|---|---|
| brainstorm / spec / plan / tasks | claude only | superpowers required |
| implement | see `.sdd/agent-assignment.json` | task-level routing |
| verify / review | claude only | sdd-reviewer subagent |

Your assigned agent for the current task is in `.sdd/state.json` → `assigned_agent`.
If the field is absent, the phase routing above applies.

## Rules for Claude (design agent)

- Do not edit source files when `.sdd/state.json` has `phase=implement` and `assigned_agent` is not `claude`.
- Before setting `phase=implement`, you MUST:
  1. Generate `specs/<feature>/handoff.md` from `orchestration/templates/handoff.md.example`.
  2. Set `assigned_agent` in `.sdd/state.json` (use `agent-assignment.json` to determine the value).
  3. Update `.sdd/tasks.json`: set the feature's `status` to `in_progress` and `handoff` to the path.
- After the implementer signals completion, set `.sdd/state.json` `phase=verify` and run `sdd-reviewer`.

## Rules for implementation agents (Codex, Gemini, etc.)

- Read `specs/<feature>/handoff.md` before touching any code.
- Implement exactly the tasks in `specs/<feature>/tasks.md`. No more, no less.
- Do NOT modify files under `specs/`, `.sdd/state.json` (phase/tier), or `orchestration/`.
- When complete, update `.sdd/tasks.json`: set your feature's `status` to `completed`.
- If the spec is wrong, ambiguous, or insufficient:
  1. Stop immediately.
  2. Set `.sdd/tasks.json` status to `blocked` and fill `blocked_reason`.
  3. Do not redesign — wait for a human to escalate to Claude.

## Handoff checklist (Claude generates before implement phase)

- [ ] `specs/<feature>/handoff.md` created from template
- [ ] `.sdd/state.json` `assigned_agent` set
- [ ] `.sdd/tasks.json` entry for this feature exists with `status: "in_progress"`
- [ ] `.sdd/state.json` `phase` set to `"implement"`
