#!/usr/bin/env bash
# SDD UserPromptSubmit reminder hook for Codex. Non-blocking context injection.
# Requires: jq.
set -euo pipefail

input="$(cat)"
root="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "${PWD}")"
state="$root/.sdd/state.json"
[ -f "$state" ] || exit 0

event="$(printf '%s' "$input" | jq -r '.hook_event_name // "UserPromptSubmit"' 2>/dev/null || printf 'UserPromptSubmit')"
tier="$(jq -r '.tier // empty' "$state" 2>/dev/null || true)"
phase="$(jq -r '.phase // empty' "$state" 2>/dev/null || true)"

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
jq -cn --arg event "$event" --arg msg "$msg" '{hookSpecificOutput:{hookEventName:$event,additionalContext:$msg}}'
