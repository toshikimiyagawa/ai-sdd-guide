#!/usr/bin/env bash
# SDD PreToolUse guard for Claude Code. A nudge, not a wall — CI is the real enforcement.
# Blocks source edits before a spec is frozen, unless the task is Tier 0.
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
if command -v jq >/dev/null 2>&1; then
  file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')"
else
  file_path="$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); ti=d.get('tool_input',{}); print(ti.get('file_path') or ti.get('path') or '')" 2>/dev/null || true)"
fi

# Always allow design/doc/state files.
case "$file_path" in
  ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*) exit 0 ;;
esac

# Block source edits from the primary checkout; linked worktrees only.
if [ "${SDD_ALLOW_MAIN_WORKTREE:-}" != "1" ] && git rev-parse --git-dir >/dev/null 2>&1; then
  git_dir="$(cd "$(git rev-parse --git-dir)" && pwd -P)"
  git_common="$(cd "$(git rev-parse --git-common-dir)" && pwd -P)"
  superproject="$(git rev-parse --show-superproject-working-tree 2>/dev/null || true)"
  if [ "$git_dir" = "$git_common" ] && [ -z "$superproject" ]; then
    {
      echo "SDD: ソース編集はリンク worktree からのみ許可されています。"
      echo "  git worktree add .worktrees/<branch> -b <branch> で worktree を作成してください。"
      echo "  メンテナンス作業の場合は SDD_ALLOW_MAIN_WORKTREE=1 を設定してください。"
    } >&2
    exit 2
  fi
fi

state=".sdd/state.json"
tier=""; phase=""
if [ -f "$state" ]; then
  tier="$(json_get "$state" "tier")"
  phase="$(json_get "$state" "phase")"
fi

# Tier must be classified before any source edit.
if [ -z "$tier" ]; then
  {
    echo "SDD: Tier が未分類です。ソース編集の前に Tier を決定してください。"
    echo "  .sdd/state.json に tier (0, 1, 2) を設定してから再試行してください。"
    echo "  参照: rules/workflow.md 'Step 0 — classify Tier'"
  } >&2
  exit 2
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
