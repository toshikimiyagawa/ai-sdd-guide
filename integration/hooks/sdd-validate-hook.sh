#!/usr/bin/env bash
# Freeze gate hook — calls sdd-validate.sh with repo root.
# Usage: sdd-validate-hook.sh [--root <path>] [extra args...]
# If --root is provided as first arg, pass all args through.
# Otherwise, resolve root via git rev-parse (fail-closed on error).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "${1:-}" = "--root" ]; then
  exec bash "$SCRIPT_DIR/../ci/sdd-validate.sh" "$@"
fi
exec bash "$SCRIPT_DIR/../ci/sdd-validate.sh" \
  --root "$(git rev-parse --show-toplevel)"
