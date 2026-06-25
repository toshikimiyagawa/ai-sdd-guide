# Issue Intake Rules (all agents)

How an issue tracker feeds the SDD workflow. Works the same on GitHub, GitLab, Bitbucket,
and Azure DevOps — only the label, dependency-link, and PR-link mechanisms differ.

## Status source of truth

`.sdd/tasks.json` is the single source of truth for SDD status, across every platform.
Visualize it with `orchestration/tools/kanban.sh` (terminal) or publish it via
`integration/ci/kanban-pages.yml` (GitHub Pages). Platform-native boards
(Projects v2, GitLab/Bitbucket Boards, Azure Work Items) are optional mirrors — never
treat a board as the canonical status.

## Always

- Do not start design or implementation until the issue carries a human-assigned
  `sdd:tier-{0,1,2}` label. The human owns the Tier decision. If it is missing, ask for it
  and stop.
- On starting an issue, add a `.sdd/tasks.json` entry: `id` = feature slug, `phase`,
  `status: "pending"`. Update `status` at every phase boundary (`in_progress` /
  `completed` / `blocked`) — this is the orchestration stop rule
  (`orchestration/rules/orchestration.md`).
- Run the Tier-appropriate flow (see `rules/workflow.md`):
  - Tier 0 — implement → PR.
  - Tier 1 — lightweight spec → implement → PR.
  - Tier 2 — spec → plan → tasks → implement → verify → PR.
- Link the PR back to the issue so merging closes it: `closes #N` (GitHub / GitLab /
  Bitbucket) or `AB#N` (Azure DevOps).
- Carry the matching `sdd:tier-{0,1,2}` label onto the PR (`rules/conventions.md`).

## Tier 2 freeze gate (check before setting phase=implement)

- Assign a stable ID to every Issue AC using the `<issue番号>-AC<連番>` format
  defined in `docs/traceability.md`. IDs are assigned in order of appearance;
  no edit to the Issue body is required.
- Create `specs/<feature>/traceability.json` mapping each Issue AC to a spec AC,
  task, and test. See `orchestration/schema/traceability.schema.json` for the schema.
- Every Issue AC must appear in an entry. If any AC is untracked, freeze is blocked.
- Entries with status `out-of-scope` or `deferred` must have a non-empty `reason`
  and an HTTP(S) `followup_issue` URL. No orphaned scope-outs allowed.
- If the frozen spec is weaker than the Issue (criteria removed or softened),
  surface a diff summary and obtain explicit human approval before freezing.

## Never

- Never implement an unlabeled issue — escalate for a Tier first.
- Never treat a platform board as the status source of truth; `.sdd/tasks.json` is canonical.
- Never expand scope beyond the issue. New scope is a new issue + a new spec.
- Never freeze a Tier 2 spec that has untracked Issue ACs or out-of-scope entries
  without a followup_issue URL.

## Per-platform mechanisms

| Concern | GitHub | GitLab | Bitbucket | Azure DevOps |
|---|---|---|---|---|
| Tier label | Labels | Labels | Labels | Tags / Area |
| Issue dependencies | Relationships (blocks / blocked by) | Linked issues | Linked issues | Links (Predecessor / Successor) |
| PR ↔ issue link | `closes #N` | `closes #N` | `closes #N` | `AB#N` |
| Status (canonical) | `.sdd/tasks.json` | `.sdd/tasks.json` | `.sdd/tasks.json` | `.sdd/tasks.json` |
| Status (optional mirror) | Projects v2 | Boards | Boards | Boards / Work Items |

Setup examples (label creation, per-platform notes): `integration/issue-tracker/`.
