#!/usr/bin/env bash
# SDD PreToolUse guard for Codex. A nudge, not a wall — CI is the real enforcement.
# Blocks detected source edits before a spec is frozen, unless the task is Tier 0.
# Requires: jq.
set -euo pipefail

input="$(cat)"
root="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "${PWD}")"
state="$root/.sdd/state.json"

tool_name="$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null || true)"
command="$(printf '%s' "$input" | jq -r '.tool_input.command // .tool_input.patch // empty' 2>/dev/null || true)"

is_exempt_path() {
  case "$1" in
    ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*) return 0 ;;
    *) return 1 ;;
  esac
}

print_context() {
  jq -cn --arg msg "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",additionalContext:$msg}}'
}

deny() {
  jq -cn --arg reason "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$reason}}'
}

join_paths() {
  printf '%b' "$1" | sed '/^$/d' | paste -sd ',' - | sed 's/,/, /g'
}

patch_paths() {
  printf '%s\n' "$command" | sed -nE \
    -e 's/^\*\*\* (Add|Update|Delete) File: //p' \
    -e 's/^\*\*\* Move to: //p' \
    -e 's/^\+\+\+ b\///p' \
    -e 's/^--- a\///p' | sed '/^\/dev\/null$/d'
}

bash_paths() {
  printf '%s\n' "$command" | grep -Eo '([A-Za-z0-9_.@+-]+/)*[A-Za-z0-9_.@+-]+\.(c|cc|cpp|css|go|h|hpp|html|java|js|json|jsx|php|py|rb|rs|scss|sh|tf|toml|ts|tsx|yaml|yml)' || true
}

looks_like_write_bash() {
  printf '%s' "$command" | grep -Eq '(apply_patch|>>?|\bsed\b[^\n]*[[:space:]]-i|\bperl\b[^\n]*[[:space:]]-pi|\b(rm|mv|cp|touch)\b)'
}

paths=""
case "$tool_name" in
  apply_patch)
    paths="$(patch_paths | sort -u)"
    ;;
  Bash)
    if printf '%s' "$command" | grep -q 'apply_patch'; then
      paths="$(patch_paths | sort -u)"
    elif looks_like_write_bash; then
      paths="$(bash_paths | sort -u)"
    else
      exit 0
    fi
    ;;
  *)
    exit 0
    ;;
esac

non_exempt=""
while IFS= read -r path; do
  [ -n "$path" ] || continue
  if ! is_exempt_path "$path"; then
    non_exempt="${non_exempt}${path}\n"
  fi
done <<EOF
$paths
EOF

if [ -z "$non_exempt" ]; then
  if [ -z "$paths" ] && [ "$tool_name" = "Bash" ] && looks_like_write_bash; then
    print_context "SDD reminder: this Bash command appears to write files. If it edits source, ensure .sdd/state.json has tier set and phase is implement or verify."
  fi
  exit 0
fi

tier=""
phase=""
if [ -f "$state" ]; then
  tier="$(jq -r '.tier // empty' "$state" 2>/dev/null || true)"
  phase="$(jq -r '.phase // empty' "$state" 2>/dev/null || true)"
fi

if [ -z "$tier" ]; then
  deny "SDD: Tier is not classified. Before editing source files, set .sdd/state.json tier to 0, 1, or 2. Detected source path(s): $(join_paths "$non_exempt")"
  exit 0
fi

[ "$tier" = "0" ] && exit 0
case "$phase" in implement|verify) exit 0 ;; esac

deny "SDD: source edits are blocked before the spec is frozen. Set .sdd/state.json phase to implement or verify, or declare Tier 0 with justification. Detected source path(s): $(join_paths "$non_exempt")"
exit 0
