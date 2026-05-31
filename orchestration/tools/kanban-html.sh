#!/usr/bin/env bash
# Render .sdd/tasks.json as a self-contained static HTML Kanban board.
# Usage: kanban-html.sh [path/to/tasks.json] [output.html]
#   - No args:    read .sdd/tasks.json, write HTML to stdout.
#   - One arg:    read given file,      write HTML to stdout.
#   - Two args:   read given file,      write HTML to the output file.
# Requires: jq. Companion to kanban.sh (terminal board); same data model.
set -euo pipefail

TASKS_FILE="${1:-.sdd/tasks.json}"
OUT="${2:-}"

if [ ! -f "$TASKS_FILE" ]; then
  echo "No tasks file found at: $TASKS_FILE" >&2
  exit 1
fi

GENERATED_AT="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"

# Emit the card fragments for one status column. Every field is HTML-escaped.
cards() {
  jq -r --arg s "$1" '
    [ .[] | select(.status == $s) ] as $col
    | if ($col | length) == 0 then
        "<p class=\"empty\">—</p>"
      else
        ( $col[]
          | "<article class=\"card\">"
            + "<div class=\"card-id\">" + (.id | @html) + "</div>"
            + "<div class=\"card-meta\">"
              + ((.assigned_agent // "—") | @html) + " · " + (.phase | @html)
            + "</div>"
            + ( if .blocked_reason then
                  "<div class=\"card-reason\">" + (.blocked_reason | @html) + "</div>"
                else "" end )
            + "</article>"
        )
      end
  ' "$TASKS_FILE"
}

TOTALS="$(jq -r '
  "Total: \(length) · pending: \([.[]|select(.status=="pending")]|length)"
  + " · in_progress: \([.[]|select(.status=="in_progress")]|length)"
  + " · completed: \([.[]|select(.status=="completed")]|length)"
  + " · blocked: \([.[]|select(.status=="blocked")]|length)"
' "$TASKS_FILE")"

PENDING="$(cards pending)"
IN_PROGRESS="$(cards in_progress)"
COMPLETED="$(cards completed)"
BLOCKED="$(cards blocked)"

render() {
  cat <<HTML
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SDD Kanban</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 1.5rem;
    font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f6f8fa; color: #1f2328;
  }
  h1 { font-size: 1.25rem; margin: 0 0 .25rem; }
  .totals { color: #57606a; margin: 0 0 1.25rem; font-variant-numeric: tabular-nums; }
  .board {
    display: grid; gap: 1rem;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
  .col {
    background: #fff; border: 1px solid #d0d7de; border-radius: 8px;
    padding: .75rem; display: flex; flex-direction: column; gap: .5rem;
  }
  .col-head {
    font-size: .75rem; font-weight: 600; letter-spacing: .04em;
    text-transform: uppercase; padding-bottom: .5rem;
    border-bottom: 2px solid var(--accent); color: var(--accent);
  }
  .col-pending     { --accent: #6e7781; }
  .col-in_progress { --accent: #0969da; }
  .col-completed   { --accent: #1a7f37; }
  .col-blocked     { --accent: #cf222e; }
  .card {
    background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px;
    padding: .5rem .6rem;
  }
  .card-id { font-weight: 600; word-break: break-word; }
  .card-meta { color: #57606a; font-size: .8rem; margin-top: .15rem; }
  .card-reason {
    margin-top: .35rem; font-size: .8rem; color: #cf222e;
    border-left: 3px solid #cf222e; padding-left: .5rem;
  }
  .empty { color: #8c959f; margin: .25rem 0; }
  footer { margin-top: 1.5rem; color: #8c959f; font-size: .8rem; }
  @media (prefers-color-scheme: dark) {
    body { background: #0d1117; color: #e6edf3; }
    .col { background: #161b22; border-color: #30363d; }
    .card { background: #0d1117; border-color: #30363d; }
    .totals, .card-meta { color: #8b949e; }
  }
</style>
</head>
<body>
<h1>SDD Kanban</h1>
<p class="totals">${TOTALS}</p>
<div class="board">
  <section class="col col-pending">
    <div class="col-head">Pending</div>
${PENDING}
  </section>
  <section class="col col-in_progress">
    <div class="col-head">In Progress</div>
${IN_PROGRESS}
  </section>
  <section class="col col-completed">
    <div class="col-head">Completed</div>
${COMPLETED}
  </section>
  <section class="col col-blocked">
    <div class="col-head">Blocked</div>
${BLOCKED}
  </section>
</div>
<footer>Generated at ${GENERATED_AT} from ${TASKS_FILE}</footer>
</body>
</html>
HTML
}

if [ -n "$OUT" ]; then
  render > "$OUT"
  echo "Wrote kanban HTML to: $OUT" >&2
else
  render
fi
