#!/usr/bin/env bash
set -euo pipefail

INTEGRATION="$(cd "$(dirname "$0")" && pwd)"
PROJECT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

log() { printf '[update.sh] %s\n' "$*"; }

# --- Managed: always overwrite ---

if [[ -d "$INTEGRATION/agents" ]]; then
  mkdir -p "$PROJECT/.claude"
  rm -rf "$PROJECT/.claude/agents"
  cp -r "$INTEGRATION/agents" "$PROJECT/.claude/agents"
  log "updated .claude/agents/"
fi

if [[ -f "$INTEGRATION/ci/sdd-check.yml" ]]; then
  mkdir -p "$PROJECT/.github/workflows"
  cp "$INTEGRATION/ci/sdd-check.yml" "$PROJECT/.github/workflows/sdd-check.yml"
  log "updated .github/workflows/sdd-check.yml"
fi

# --- Protected: create if absent, diff if changed ---

protected=(
  "CLAUDE.md:$INTEGRATION/CLAUDE.md.example"
  "AGENTS.md:$INTEGRATION/AGENTS.md.example"
  ".claude/settings.json:$INTEGRATION/settings.json.example"
)

for entry in "${protected[@]}"; do
  rel="${entry%%:*}"
  src="${entry#*:}"
  dest="$PROJECT/$rel"

  if [[ ! -f "$src" ]]; then continue; fi

  if [[ ! -f "$dest" ]]; then
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    log "created $rel (was absent)"
  elif ! diff -q "$src" "$dest" >/dev/null 2>&1; then
    log "diff (protected — review manually): $rel"
    diff "$dest" "$src" || true
  fi
done

log "done"
