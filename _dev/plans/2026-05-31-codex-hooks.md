# Codex Hooks Integration Plan

**Goal:** Add Codex CLI hook support to ai-sdd-guide while preserving existing Claude Code integration.

**Architecture:** Provide a project-local Codex config template plus two hook scripts. `update.sh` treats `.codex/config.toml` as protected config, mirroring `.claude/settings.json` behavior.

**Tech Stack:** Bash, jq, Codex lifecycle hooks, Markdown.

---

### Task 1: Add Codex hook template

**Files:**
- Create: `integration/codex/config.toml.example`

- [x] Define `[features].hooks = true`.
- [x] Add `PreToolUse` hook for `apply_patch` and `Bash`.
- [x] Add `UserPromptSubmit` hook for phase reminders.

### Task 2: Add Codex SDD guard

**Files:**
- Create: `integration/hooks/codex-sdd-guard.sh`

- [x] Read Codex hook JSON from stdin.
- [x] Detect source paths from `apply_patch` patch headers.
- [x] Detect common Bash write patterns conservatively.
- [x] Deny detected source edits when Tier is missing or phase is before implement/verify.
- [x] Allow Tier 0 and design/doc/state paths.

### Task 3: Add Codex phase reminder

**Files:**
- Create: `integration/hooks/codex-skill-reminder.sh`

- [x] Read `.sdd/state.json`.
- [x] Return Codex `additionalContext` JSON for the current SDD phase.
- [x] Skip Tier 0 and irrelevant Tier 1 design-phase reminders.

### Task 4: Integrate with update flow and docs

**Files:**
- Modify: `integration/update.sh`
- Modify: `integration/AGENTS.md.example`
- Modify: `README.md`

- [x] Add `.codex/config.toml` as protected config.
- [x] Document setup and update behavior.
- [x] Note that Codex hooks require `/hooks` review/trust after install or changes.

### Task 5: Verify

- [x] `bash -n` on hook scripts and `update.sh`.
- [x] Guard denies source edits when Tier is missing.
- [x] Guard allows docs edits and Tier 0 edits.
- [x] Guard denies source edits in pre-implementation phase.
- [x] Reminder emits Codex `additionalContext` JSON.
- [x] `update.sh` creates `.codex/config.toml` in a fresh project.
