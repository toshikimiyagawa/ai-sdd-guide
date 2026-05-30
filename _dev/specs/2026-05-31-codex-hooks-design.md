# Design: Codex Hooks Integration

**Date:** 2026-05-31
**Status:** Approved

## Overview

Add Codex CLI lifecycle hook support alongside the existing Claude Code hooks. The goal is to provide the same local SDD guardrail shape for Codex users without changing the CI contract: local hooks are fast nudges, while CI remains the authoritative enforcement layer.

## Requirements

- Provide a repo-local Codex hook template that consuming projects can copy to `.codex/config.toml`.
- Block detected source edits before Tier classification or before the spec is frozen.
- Keep docs/specs/SDD state edits unblocked so agents can create or update the design artifacts needed to proceed.
- Inject non-blocking SDD phase reminders into Codex developer context.
- Do not overwrite existing project-local Codex config during updates; create it only when absent and show a diff otherwise.
- Preserve the existing Claude hook integration.

## Design

Add `integration/codex/config.toml.example` with two hooks:

- `PreToolUse` for `apply_patch` and `Bash`, calling `codex-sdd-guard.sh`.
- `UserPromptSubmit`, calling `codex-skill-reminder.sh`.

`codex-sdd-guard.sh` reads Codex hook JSON from stdin. For `apply_patch`, it extracts changed paths from patch headers. For `Bash`, it conservatively detects common file-writing command shapes and extracts likely file paths. If no source path can be determined, it only injects context rather than blocking.

`codex-skill-reminder.sh` reads `.sdd/state.json` and returns Codex `additionalContext` JSON for the current Tier/phase.

## Limitations

Codex hooks are not a complete enforcement boundary. They only cover hook-supported tool paths and Codex may perform equivalent work through paths not intercepted by `PreToolUse`. CI remains the non-bypassable gate.
