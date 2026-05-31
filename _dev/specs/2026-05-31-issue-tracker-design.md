# Design: Issue Tracker Integration (SDD Intake Flow)

**Date:** 2026-05-31
**Status:** Approved
**Issue:** #19

## Overview

Define how an issue tracker (GitHub / GitLab / Bitbucket / Azure DevOps) feeds the SDD
workflow: from issue registration, through Tier classification and the SDD phases, to PR
merge and issue closure.

**Status source of truth is unified to `.sdd/tasks.json` (the SDD kanban from #18).**
Platform-native boards (Projects v2, GitLab/Bitbucket Boards, Azure Work Items) are optional
mirrors only. This keeps status identical across trackers and reuses the kanban already
published via `kanban.sh` (terminal) and `kanban-pages.yml` (GitHub Pages).

## Requirements

- Add an agent rule file `rules/issue-intake.md` (English, imperative) covering:
  - Read the issue; require a human-assigned `sdd:tier-{0,1,2}` label before design/implementation.
  - Register/track the feature in `.sdd/tasks.json` — the status source of truth — across all phases.
  - Run the Tier-appropriate SDD flow; link the PR back to the issue (`closes #N`, or `AB#N` for Azure).
  - Treat platform-native boards as optional mirrors, never the source of truth.
- Add a human-facing Japanese doc `docs/04-issue-tracker.md` with the platform feature
  mapping table, registration rules, the intake→completion flow, and the status-management
  policy (kanban is canonical).
- Add consuming-project setup examples under `integration/issue-tracker/`:
  - `labels.sh` — create the three tier labels on GitHub via `gh` (idempotent).
  - `README.md` — per-platform setup (GitHub / GitLab / Bitbucket / Azure DevOps).
- Wire the new rule into `AGENTS.md` read list and reference the integration in `README.md`.
- Do not duplicate Tier definitions; reference existing `rules/workflow.md`.

## Design

The intake flow layers on top of the existing workflow without changing it:

```
Issue registered → human assigns sdd:tier-N label
  → agent reads the issue, adds a .sdd/tasks.json entry (status=pending)   ← source of truth
  → Tier 0: implement → PR(closes #N)
    Tier 1: lightweight spec → implement → PR
    Tier 2: spec → plan → tasks → implement → verify → PR
  → status updated in tasks.json at each phase boundary (orchestration stop rule)
  → PR merged → tasks.json completed → issue closed
```

Only three things differ per platform: the label mechanism, the dependency-link mechanism,
and the PR↔issue link syntax. The mapping table documents these. Everything else — Tier
rules, SDD phases, and status tracked in `.sdd/tasks.json` — is identical.

`integration/issue-tracker/labels.sh` uses `gh label create --force` so it is safe to
re-run. Non-GitHub platforms get documented manual/CLI steps in the README rather than
scripts, since their CLIs differ and are out of this repo's core toolchain.

## Out of scope

- Automating issue creation or board syncing on non-GitHub platforms.
- A live two-way sync between `.sdd/tasks.json` and platform boards.
- Changing the Tier model or the SDD phase definitions.

## Limitations

The unified status lives in `.sdd/tasks.json`; platform-native boards, if used, must be
updated separately (this repo does not sync them). Azure DevOps uses `AB#N` instead of
`closes #N` for PR↔work-item linking.
