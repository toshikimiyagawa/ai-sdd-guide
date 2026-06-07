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
  hook_cwd="$(printf '%s' "$input" | jq -r '.cwd // .tool_input.cwd // empty')"
else
  file_path="$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); ti=d.get('tool_input',{}); print(ti.get('file_path') or ti.get('path') or '')" 2>/dev/null || true)"
  hook_cwd="$(printf '%s' "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('cwd') or d.get('tool_input',{}).get('cwd') or '')" 2>/dev/null || true)"
fi

# Always allow design/doc/state files.
case "$file_path" in
  ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*) exit 0 ;;
esac

invocation_root="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "${PWD}")"
base_dir="${hook_cwd:-$invocation_root}"

resolve_path() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s/%s\n' "$base_dir" "$1" ;;
  esac
}

existing_parent() {
  local target="$1" dir
  if [ -d "$target" ]; then
    dir="$target"
  else
    dir="$(dirname "$target")"
  fi
  while [ ! -d "$dir" ] && [ "$dir" != "/" ]; do
    dir="$(dirname "$dir")"
  done
  printf '%s\n' "$dir"
}

git_abs_path() {
  local root="$1" git_path="$2"
  case "$git_path" in
    /*) printf '%s\n' "$git_path" ;;
    *) printf '%s/%s\n' "$root" "$git_path" ;;
  esac
}

# Resolve the repo/worktree root of the edit target, not the hook's cwd.
repo_root_for_path() {
  local path dir
  path="$(resolve_path "$1")"
  dir="$(existing_parent "$path")"
  git -C "$dir" rev-parse --show-toplevel 2>/dev/null || printf '%s\n' "$invocation_root"
}

target_root="$(repo_root_for_path "$file_path")"

# Block source edits from the primary checkout; linked worktrees only.
if [ "${SDD_ALLOW_MAIN_WORKTREE:-}" != "1" ] && git -C "$target_root" rev-parse --git-dir >/dev/null 2>&1; then
  git_dir="$(git_abs_path "$target_root" "$(git -C "$target_root" rev-parse --git-dir)")"
  git_common="$(git_abs_path "$target_root" "$(git -C "$target_root" rev-parse --git-common-dir)")"
  git_dir="$(cd "$git_dir" && pwd -P)"
  git_common="$(cd "$git_common" && pwd -P)"
  superproject="$(git -C "$target_root" rev-parse --show-superproject-working-tree 2>/dev/null || true)"
  if [ "$git_dir" = "$git_common" ] && [ -z "$superproject" ]; then
    {
      echo "SDD: ソース編集はリンク worktree からのみ許可されています。"
      echo "  git worktree add .worktrees/<branch> -b <branch> で worktree を作成してください。"
      echo "  メンテナンス作業の場合は SDD_ALLOW_MAIN_WORKTREE=1 を設定してください。"
    } >&2
    exit 2
  fi
fi

state="$target_root/.sdd/state.json"
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
