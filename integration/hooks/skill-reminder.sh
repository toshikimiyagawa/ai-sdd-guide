#!/usr/bin/env bash
# SDD skill reminder hook for Claude Code. Non-blocking nudge — reminds Claude which superpowers skill belongs to the current SDD phase.
# Tier 0 is skipped (no design overhead). Tier 1 reminds only for implement/verify. Tier 2 reminds across all design phases.
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

# Drain stdin (tool input); we don't read it.
cat >/dev/null

state=".sdd/state.json"
[ -f "$state" ] || exit 0

tier="$(json_get "$state" "tier")"
phase="$(json_get "$state" "phase")"

# Tier 0: trivial work, no skill required.
[ "$tier" = "0" ] && exit 0
[ -z "$tier" ] || [ -z "$phase" ] && exit 0

# Tier 1: skip design-phase reminders; only implement/verify reminders apply.
if [ "$tier" = "1" ]; then
  case "$phase" in implement|verify) ;; *) exit 0 ;; esac
fi

case "$phase" in
  brainstorm)
    echo "SDD reminder: brainstorm phase — invoke skill 'brainstorming' (Skill tool) before drafting the spec." >&2
    ;;
  spec)
    echo "SDD reminder: spec phase — capture brainstorm output into specs/<feature>/spec.md with checkable acceptance criteria. Get human approval before freezing." >&2
    ;;
  plan|tasks)
    echo "SDD reminder: $phase phase — invoke skill 'writing-plans' (Skill tool). For parallelism consider 'dispatching-parallel-agents'." >&2
    ;;
  implement)
    echo "SDD reminder: implement phase — invoke skills 'executing-plans' + 'test-driven-development' + 'systematic-debugging' before editing source." >&2
    ;;
  verify)
    echo "SDD reminder: verify phase — invoke 'verification-before-completion'. Use 'receiving-code-review' for any review feedback; spec-conflicting feedback must escalate, not silently absorb." >&2
    ;;
esac
exit 0
