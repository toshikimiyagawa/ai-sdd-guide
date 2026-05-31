# Issue Tracker Setup

Per-platform setup for the SDD intake flow. The flow itself is identical everywhere; only
the label, dependency-link, and PR-link mechanisms differ. See `rules/issue-intake.md`
(agent rule) and `docs/04-issue-tracker.md` (human guide).

**Status is always tracked in `.sdd/tasks.json` (the SDD kanban), not in platform boards.**
Boards are optional mirrors only.

## GitHub (baseline)

Create the three Tier labels (idempotent):

```bash
bash vendor/ai-sdd-guide/integration/issue-tracker/labels.sh           # current repo
bash vendor/ai-sdd-guide/integration/issue-tracker/labels.sh owner/repo
```

- Dependencies: link issues with **Relationships** (blocks / blocked by).
- PR ↔ issue: put `closes #N` in the PR description.

## GitLab

- Tier labels: create `sdd::tier-0/1/2` (scoped labels) under **Project → Labels**, or via
  `glab label create --name "sdd:tier-2" --color "#d93f0b"`.
- Dependencies: **Linked issues** (blocks / is blocked by).
- MR ↔ issue: `Closes #N` in the MR description.

## Bitbucket

- Tier labels: Bitbucket issues have no native labels — use the issue **Kind/Priority**
  fields or a `sdd:tier-N` token in the title/component, depending on your plan.
- Dependencies: **Linked issues**.
- PR ↔ issue: `closes #N` in the PR description.

## Azure DevOps

- Tier labels: apply **Tags** `sdd:tier-0/1/2` (or an **Area** path) to the Work Item.
- Dependencies: **Links** → Predecessor / Successor.
- PR ↔ work item: reference `AB#N` in the PR description or a commit message.

---

After labels exist, the agent follows `rules/issue-intake.md`: read the labeled issue,
register it in `.sdd/tasks.json`, run the Tier-appropriate SDD flow, and link the PR back.
