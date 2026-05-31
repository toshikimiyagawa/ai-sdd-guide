# Issue Tracker Integration Plan

**Goal:** Define the Issue → SDD intake flow for GitHub / GitLab / Bitbucket / Azure DevOps, with `.sdd/tasks.json` (the #18 SDD kanban) as the unified status source of truth. (Issue #19)

**Architecture:** One agent rule file (`rules/issue-intake.md`), one human doc (`docs/04-issue-tracker.md`), and consuming-project setup examples (`integration/issue-tracker/`). The flow reuses the existing Tier model and SDD phases; only label/dependency/PR-link mechanisms differ per platform.

**Tech Stack:** Markdown, Bash, `gh` CLI (GitHub label script).

---

### Task 1: Agent rule — issue intake

**Files:**
- Create: `rules/issue-intake.md`

- [ ] Require a human-assigned `sdd:tier-{0,1,2}` label before design/implementation; escalate if missing.
- [ ] Register the feature in `.sdd/tasks.json` (status source of truth) and update it at each phase boundary.
- [ ] Run the Tier-appropriate SDD flow; link the PR (`closes #N`, `AB#N` for Azure).
- [ ] State that platform-native boards are optional mirrors, never canonical.
- [ ] Reference `rules/workflow.md` for Tier defs (no duplication).

### Task 2: Human doc — issue tracker integration

**Files:**
- Create: `docs/04-issue-tracker.md`

- [ ] Platform feature mapping table (Tier labels / dependencies / PR link / status).
- [ ] Registration rules (GitHub baseline + other 3).
- [ ] Intake → completion flow diagram.
- [ ] Status-management policy: `.sdd/tasks.json` canonical, kanban for visualization (#18).

### Task 3: Consuming-project setup examples

**Files:**
- Create: `integration/issue-tracker/labels.sh`
- Create: `integration/issue-tracker/README.md`

- [ ] `labels.sh`: idempotent `gh label create --force` for the three tier labels.
- [ ] README: per-platform setup (GitHub / GitLab / Bitbucket / Azure DevOps).

### Task 4: Wire into entry points

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`

- [ ] Add `rules/issue-intake.md` to the AGENTS.md read list.
- [ ] Reference the issue-tracker integration (doc + integration dir) in README.

### Task 5: Verify

- [ ] `bash -n integration/issue-tracker/labels.sh`.
- [ ] Mapping table renders; all 4 platforms present in doc + rule.
- [ ] Status source-of-truth (`.sdd/tasks.json`) stated in rule + doc; boards marked optional.
- [ ] Tier defs referenced, not duplicated.
- [ ] Links between README ↔ doc ↔ rule resolve to real paths.
