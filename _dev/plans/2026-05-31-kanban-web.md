# Kanban Web Visualization Plan

**Goal:** Publish `.sdd/tasks.json` as a static HTML kanban via a new tool + GitHub Pages workflow, without changing `kanban.sh`. (Issue #18)

**Architecture:** A standalone bash+jq renderer in `orchestration/tools/` mirrors `kanban.sh`'s data model and column layout but emits a self-contained HTML page. A copy-able GitHub Actions workflow in `integration/ci/` generates the page and deploys it to GitHub Pages.

**Tech Stack:** Bash, jq, GitHub Actions, GitHub Pages, HTML/CSS.

---

### Task 1: Add the HTML renderer

**Files:**
- Create: `orchestration/tools/kanban-html.sh`

- [ ] Usage `kanban-html.sh [tasks.json] [output.html]`; default input `.sdd/tasks.json`, default output stdout.
- [ ] Error with non-zero exit when the input file is missing.
- [ ] jq emits per-column card fragments, every field escaped with `@html`; null `assigned_agent` → `—`.
- [ ] Blocked cards render `blocked_reason`.
- [ ] Totals line uses the same jq shape as `kanban.sh`.
- [ ] Assemble a self-contained HTML doc (inline CSS, four columns, UTC generated-at).

### Task 2: Add the GitHub Pages workflow example

**Files:**
- Create: `integration/ci/kanban-pages.yml`

- [ ] Triggers: `push` (paths `.sdd/tasks.json`) + `workflow_dispatch`.
- [ ] Permissions `pages: write`, `id-token: write`; `concurrency: pages`.
- [ ] Build job runs the vendored `kanban-html.sh` into `_site/index.html`, with a placeholder fallback when `tasks.json` is absent.
- [ ] Deploy job uses `upload-pages-artifact` + `deploy-pages`.

### Task 3: Document the tool and publish step

**Files:**
- Modify: `README.md`
- Modify: `orchestration/rules/orchestration.md`

- [ ] Add `kanban-html.sh` to the orchestration component table.
- [ ] Add a "Web 可視化" subsection (usage + CI copy step).
- [ ] Mention the HTML renderer in `orchestration.md` near the kanban display rule.

### Task 4: Verify

- [ ] `bash -n orchestration/tools/kanban-html.sh`.
- [ ] Render a sample `tasks.json` (incl. a blocked task + null agent) → valid HTML with all columns, cards, reason, totals.
- [ ] Missing input file exits non-zero with a clear message.
- [ ] HTML escaping: a task field containing `<script>` is escaped in output.
- [ ] `kanban.sh` is unchanged (`git diff` clean for it).
- [ ] Lint the workflow YAML (parse check).
