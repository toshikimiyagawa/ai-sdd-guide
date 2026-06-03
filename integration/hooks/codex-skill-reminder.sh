#!/usr/bin/env bash
# SDD UserPromptSubmit reminder hook for Codex. Non-blocking context injection.
# Prefers jq; falls back to python3.
set -euo pipefail

json_get() {
  local file="$1" key="$2"
  if command -v jq >/dev/null 2>&1; then
    jq -r ".${key} // empty" "$file" 2>/dev/null || true
  else
    python3 -c "import json; d=json.load(open('$file')); print(d.get('$key') or '')" 2>/dev/null || true
  fi
}

input="$(cat)"
root="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "${PWD}")"
state="$root/.sdd/state.json"
[ -f "$state" ] || exit 0

if command -v jq >/dev/null 2>&1; then
  event="$(printf '%s' "$input" | jq -r '.hook_event_name // "UserPromptSubmit"' 2>/dev/null || printf 'UserPromptSubmit')"
else
  event="$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('hook_event_name') or 'UserPromptSubmit')" 2>/dev/null || printf 'UserPromptSubmit')"
fi
tier="$(json_get "$state" "tier")"
phase="$(json_get "$state" "phase")"

[ "$tier" = "0" ] && exit 0
[ -z "$tier" ] || [ -z "$phase" ] && exit 0

if [ "$tier" = "1" ]; then
  case "$phase" in implement|verify) ;; *) exit 0 ;; esac
fi

msg=""
case "$phase" in
  brainstorm)
    msg="SDD reminder: brainstorm phase. Use the superpowers 'brainstorming' skill before drafting the spec; if this agent cannot use it, stop and hand off design work."
    ;;
  spec)
    msg="SDD reminder: spec phase. Capture brainstorm output into specs/<feature>/spec.md with checkable acceptance criteria, then get human approval before freezing."
    ;;
  plan|tasks)
    msg="SDD reminder: ${phase} phase. Use the superpowers 'writing-plans' skill; for parallel work consider dispatching parallel agents."
    ;;
  implement)
    msg="SDD reminder: implement phase. Implement only the frozen specs/<feature>/tasks.md; every acceptance criterion must map to a passing test. Do not modify specs/ to fit implementation."
    ;;
  verify)
    msg="SDD reminder: verify phase. Run the sdd-reviewer prompt/subagent against the diff. Review feedback that expands scope must escalate to a new spec, not be silently absorbed."
    ;;
esac

[ -n "$msg" ] || exit 0
if command -v jq >/dev/null 2>&1; then
  jq -cn --arg event "$event" --arg msg "$msg" '{hookSpecificOutput:{hookEventName:$event,additionalContext:$msg}}'
else
  python3 -c "import json,sys; print(json.dumps({'hookSpecificOutput':{'hookEventName':sys.argv[1],'additionalContext':sys.argv[2]}}))" "$event" "$msg"
fi
