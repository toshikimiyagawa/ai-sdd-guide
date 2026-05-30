#!/usr/bin/env bash
# Display .sdd/tasks.json as a text Kanban board.
# Usage: kanban.sh [path/to/tasks.json]
# Requires: jq.
set -euo pipefail

TASKS_FILE="${1:-.sdd/tasks.json}"

if [ ! -f "$TASKS_FILE" ]; then
  echo "No tasks file found at: $TASKS_FILE"
  exit 0
fi

COL=24
SEP="$(printf '─%.0s' $(seq 1 $((COL - 1))))"

get_tasks() {
  jq -r --arg s "$1" \
    '.[] | select(.status == $s) | .id + "  [" + .assigned_agent + "/" + .phase + "]"' \
    "$TASKS_FILE"
}

pending=()
in_progress=()
completed=()
blocked_tasks=()

while IFS= read -r line; do [ -n "$line" ] && pending+=("$line"); done      < <(get_tasks "pending")
while IFS= read -r line; do [ -n "$line" ] && in_progress+=("$line"); done  < <(get_tasks "in_progress")
while IFS= read -r line; do [ -n "$line" ] && completed+=("$line"); done    < <(get_tasks "completed")
while IFS= read -r line; do [ -n "$line" ] && blocked_tasks+=("$line"); done < <(get_tasks "blocked")

rows=${#pending[@]}
[ ${#in_progress[@]} -gt "$rows" ] && rows=${#in_progress[@]}
[ ${#completed[@]} -gt "$rows" ]   && rows=${#completed[@]}
[ ${#blocked_tasks[@]} -gt "$rows" ] && rows=${#blocked_tasks[@]}

echo ""
printf "%-${COL}s  %-${COL}s  %-${COL}s  %-${COL}s\n" "PENDING" "IN_PROGRESS" "COMPLETED" "BLOCKED"
printf "%-${COL}s  %-${COL}s  %-${COL}s  %-${COL}s\n" "$SEP" "$SEP" "$SEP" "$SEP"

for ((i = 0; i < rows; i++)); do
  printf "%-${COL}s  %-${COL}s  %-${COL}s  %-${COL}s\n" \
    "${pending[$i]:-}" \
    "${in_progress[$i]:-}" \
    "${completed[$i]:-}" \
    "${blocked_tasks[$i]:-}"
done

echo ""
jq -r '"Total: \(length) | pending:\([.[]|select(.status=="pending")]|length)  in_progress:\([.[]|select(.status=="in_progress")]|length)  completed:\([.[]|select(.status=="completed")]|length)  blocked:\([.[]|select(.status=="blocked")]|length)"' \
  "$TASKS_FILE"
echo ""
