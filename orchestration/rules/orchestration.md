# Orchestration Rules (all agents)

## Scope assignment

All phases are open to any agent with superpowers installed. The human decides which agent handles which phase.

| Phase | Requirement | Notes |
|---|---|---|
| brainstorm / spec / plan / tasks | superpowers required | Any agent (Claude, Codex, Gemini) |
| implement | none | Any agent; human assigns explicitly |
| verify | superpowers required | Use sdd-reviewer (see below) |

## Phase stopping rule

Every agent MUST stop after completing a phase and wait for explicit human instruction before starting the next phase. Never cross a phase boundary automatically.

- Design complete (tasks.md created): generate handoff.md → update tasks.json → display kanban → stop. Do NOT start implementing.
- Task implementation complete: commit → update tasks.json → display kanban → stop. Do NOT start verify.
- Verify complete: report results → display kanban → stop.

Display kanban by running:
```bash
bash vendor/ai-sdd-guide/orchestration/tools/kanban.sh
```

For a shareable web view, `orchestration/tools/kanban-html.sh` renders the same
`.sdd/tasks.json` as a self-contained static HTML page (auto-published via
`integration/ci/kanban-pages.yml` on GitHub Pages).

## Rules for design agents (brainstorm/spec/plan/tasks)

- Use superpowers: brainstorming → writing-plans skills.
- At end of tasks phase, generate `specs/<feature>/handoff.md` from `orchestration/templates/handoff.md.example`.
- Update `.sdd/tasks.json`: add the feature entry with `id` (feature slug), `phase: "tasks"`, `status: "pending"`, and optionally `handoff: null`.
- Display kanban and stop.

## Rules for implementation agents

- Read `specs/<feature>/handoff.md` before touching any code.
- Implement exactly the tasks in `specs/<feature>/tasks.md`. No more, no less.
- Do NOT modify files under `specs/`, `.sdd/state.json` (phase/tier), or `orchestration/`.
- When complete, update `.sdd/tasks.json`: set your feature's `status` to `"completed"`.
- Display kanban and stop.
- If the spec is wrong, ambiguous, or insufficient:
  1. Stop immediately.
  2. Set `.sdd/tasks.json` status to `"blocked"` and fill `blocked_reason`.
  3. Do not redesign — wait for a human to escalate.

## Running sdd-reviewer (verify phase)

**Claude Code:** Use the `sdd-reviewer` subagent (`.claude/agents/sdd-reviewer.md`).

**Gemini CLI:** Pass the contents of `vendor/ai-sdd-guide/integration/prompts/sdd-reviewer-prompt.md` to `@generalist`.

**Codex:** Pass the contents of `vendor/ai-sdd-guide/integration/prompts/sdd-reviewer-prompt.md` to `spawn_agent`.

**Independent Reviewer Requirement**:
- No matter which agent performs design/implementation, the verify phase MUST invoke the `sdd-reviewer` subagent.
- `sdd-reviewer` acts as an independent third party, verifying the diff vs spec from a different context than the implementation agent.
- An adversarial review by an independent reviewer is a mandatory step before handoff is complete.
