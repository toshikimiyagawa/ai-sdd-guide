#!/usr/bin/env bash
# Create the SDD Tier labels on a GitHub repository. Idempotent (safe to re-run).
# Usage: labels.sh [owner/repo]   (defaults to the current repo via gh)
# Requires: gh (GitHub CLI), authenticated.
set -euo pipefail

REPO="${1:-}"
ARGS=()
[ -n "$REPO" ] && ARGS=(--repo "$REPO")

if ! command -v gh >/dev/null 2>&1; then
  echo "gh (GitHub CLI) is required: https://cli.github.com/" >&2
  exit 1
fi

create() {
  # --force updates the label if it already exists, so re-runs are safe.
  gh label create "$1" --color "$2" --description "$3" --force "${ARGS[@]}"
}

create "sdd:tier-0" "cccccc" "SDD Tier 0 — trivial; no spec required"
create "sdd:tier-1" "fbca04" "SDD Tier 1 — small change; lightweight spec + tests"
create "sdd:tier-2" "d93f0b" "SDD Tier 2 — medium/large; full spec → plan → tasks → verify"

echo "SDD tier labels created/updated."
