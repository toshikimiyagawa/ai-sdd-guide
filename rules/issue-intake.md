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

## Never

- Never implement an unlabeled issue — escalate for a Tier first.
- Never treat a platform board as the status source of truth; `.sdd/tasks.json` is canonical.
- Never expand scope beyond the issue. New scope is a new issue + a new spec.

## Per-platform mechanisms

| Concern | GitHub | GitLab | Bitbucket | Azure DevOps |
|---|---|---|---|---|
| Tier label | Labels | Labels | Labels | Tags / Area |
| Issue dependencies | Relationships (blocks / blocked by) | Linked issues | Linked issues | Links (Predecessor / Successor) |
| PR ↔ issue link | `closes #N` | `closes #N` | `closes #N` | `AB#N` |
| Status (canonical) | `.sdd/tasks.json` | `.sdd/tasks.json` | `.sdd/tasks.json` | `.sdd/tasks.json` |
| Status (optional mirror) | Projects v2 | Boards | Boards | Boards / Work Items |

Setup examples (label creation, per-platform notes): `integration/issue-tracker/`.
