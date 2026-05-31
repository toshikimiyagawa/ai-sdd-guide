# Design: Web Visualization of SDD Kanban

**Date:** 2026-05-31
**Status:** Approved
**Issue:** #18

## Overview

`orchestration/tools/kanban.sh` renders `.sdd/tasks.json` only as a terminal board.
Add a separate tool that renders the same data as a self-contained static HTML page,
plus a GitHub Actions + GitHub Pages workflow example so consuming projects can publish
the latest kanban at a URL on every push.

`kanban.sh` is not modified — HTML generation is a new, single-responsibility script.

## Requirements

- Add `orchestration/tools/kanban-html.sh` that reads `.sdd/tasks.json` and emits a
  self-contained HTML kanban board (no external CSS/JS/font dependencies).
- The HTML must show the same four columns as `kanban.sh`
  (PENDING / IN_PROGRESS / COMPLETED / BLOCKED), each task's `id`, `assigned_agent`,
  and `phase`, the `blocked_reason` for blocked tasks, and the totals line.
- Task field values must be HTML-escaped (no injection from `tasks.json` content).
- The script writes to stdout by default and to a file when an output path is given.
- Missing input file is a clear error (non-zero exit), matching tooling conventions.
- Add `integration/ci/kanban-pages.yml`: a workflow example consuming projects copy to
  `.github/workflows/`. On push it generates the HTML and deploys to GitHub Pages.
- Document the tool and the publish step in `README.md` and `orchestration/rules/orchestration.md`.
- Do not modify `kanban.sh`.

## Design

`kanban-html.sh` (bash + jq):

- Usage: `kanban-html.sh [path/to/tasks.json] [output.html]`. Default input
  `.sdd/tasks.json`; default output stdout.
- A jq program emits card fragments per status column, escaping every field with `@html`.
  `assigned_agent` null renders as `—`. Blocked cards include `blocked_reason`.
- Totals are computed with the same jq shape as `kanban.sh` for parity.
- The bash wrapper assembles a single HTML document with inline CSS (four colored
  columns, responsive grid) and a UTC "generated at" timestamp.

`integration/ci/kanban-pages.yml`:

- Triggers: `push` (paths filter on `.sdd/tasks.json`) and `workflow_dispatch`.
- Permissions `pages: write` + `id-token: write`; `concurrency` group `pages`.
- Build job runs `vendor/ai-sdd-guide/orchestration/tools/kanban-html.sh` into `_site/index.html`
  (vendored path, consistent with how `kanban.sh` is referenced), falling back to a
  placeholder page when `.sdd/tasks.json` is absent. Deploy job uses `actions/deploy-pages`.

## Out of scope (per issue #18)

- Real-time updates.
- External service integration (Grafana, etc.).
- Authentication / access control.

## Limitations

The published page is a static snapshot regenerated on push; it is not live. GitHub Pages
must be enabled with "GitHub Actions" as the source in the consuming repository before the
workflow can deploy.
