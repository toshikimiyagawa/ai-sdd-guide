#!/usr/bin/env bash
# SDD PreToolUse guard for Claude Code. A nudge, not a wall — CI is the real enforcement.
# Blocks source edits before a spec is frozen, unless the task is Tier 0.
# Requires: jq.
set -euo pipefail

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')"

# Always allow design/doc/state files.
case "$file_path" in
  ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*) exit 0 ;;
esac

state=".sdd/state.json"
tier=""; phase=""
if [ -f "$state" ]; then
  tier="$(jq -r '.tier // empty' "$state" 2>/dev/null || true)"
  phase="$(jq -r '.phase // empty' "$state" 2>/dev/null || true)"
fi

# Tier 0 is exempt.
[ "$tier" = "0" ] && exit 0
# Allowed once the spec is frozen and we are implementing/verifying.
case "$phase" in implement|verify) exit 0 ;; esac

{
  echo "SDD: source edits to '$file_path' are blocked before the spec is frozen."
  echo "Do one of:"
  echo "  (a) create specs/<feature>/ and set .sdd/state.json phase=implement, or"
  echo "  (b) declare Tier 0 in .sdd/state.json with a one-line justification."
} >&2
exit 2
