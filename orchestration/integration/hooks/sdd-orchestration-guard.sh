#!/usr/bin/env bash
# SDD Orchestration guard (Claude Code PreToolUse hook).
# Prevents Claude from editing source files when the current implement task
# is assigned to a different agent.
# Non-blocking on missing config — this is an opt-in feature.
# Requires: jq.
set -euo pipefail

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')"

# Always allow: design artifacts, state files, orchestration config.
case "$file_path" in
  ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*|orchestration/*|*/orchestration/*) exit 0 ;;
esac

state=".sdd/state.json"
[ -f "$state" ] || exit 0

phase="$(jq -r '.phase // empty' "$state" 2>/dev/null || true)"
assigned_agent="$(jq -r '.assigned_agent // empty' "$state" 2>/dev/null || true)"

# Only enforce during implement phase.
[ "$phase" = "implement" ] || exit 0

# No assigned_agent field means orchestration is not active — allow.
[ -z "$assigned_agent" ] && exit 0

# Assigned to Claude — allow.
[ "$assigned_agent" = "claude" ] && exit 0

# Another agent is assigned — block Claude from editing source.
printf 'SDD Orchestration: この実装タスクは "%s" に割り当てられています。\n' "$assigned_agent" >&2
printf 'Claude はソース編集できません。\n' >&2
printf 'Claude に変更するには .sdd/state.json の assigned_agent を "claude" に設定してください。\n' >&2
exit 2
