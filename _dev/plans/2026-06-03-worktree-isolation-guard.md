# Worktree Isolation Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a primary-checkout guard to `sdd-guard.sh` and `codex-sdd-guard.sh`, and document the hook behavior in a new `README.md`.

**Architecture:** Three independent file edits. Each adds/modifies exactly one file. No shared state between tasks.

**Tech Stack:** Bash, Markdown.

---

### Task 1: Add worktree isolation check to `sdd-guard.sh`

**Files:**
- Modify: `integration/hooks/sdd-guard.sh`

The check must be inserted **after** the exempt-path `case` block and **before** the `state=".sdd/state.json"` line.

Current code at that position:
```bash
# Always allow design/doc/state files.
case "$file_path" in
  ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*) exit 0 ;;
esac

state=".sdd/state.json"
```

- [ ] **Step 1: Insert the worktree check**

Find and replace the exact string above with:

```bash
# Always allow design/doc/state files.
case "$file_path" in
  ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*) exit 0 ;;
esac

# Block source edits from the primary checkout; linked worktrees only.
if [ "${SDD_ALLOW_MAIN_WORKTREE:-}" != "1" ]; then
  git_dir="$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P || true)"
  git_common="$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P || true)"
  superproject="$(git rev-parse --show-superproject-working-tree 2>/dev/null || true)"
  if [ -n "$git_dir" ] && [ "$git_dir" = "$git_common" ] && [ -z "$superproject" ]; then
    {
      echo "SDD: ソース編集はリンク worktree からのみ許可されています。"
      echo "  git worktree add .worktrees/<branch> -b <branch> で worktree を作成してください。"
      echo "  メンテナンス作業の場合は SDD_ALLOW_MAIN_WORKTREE=1 を設定してください。"
    } >&2
    exit 2
  fi
fi

state=".sdd/state.json"
```

- [ ] **Step 2: Syntax check**

```bash
bash -n integration/hooks/sdd-guard.sh
```
Expected: no output (syntax OK).

- [ ] **Step 3: Commit**

```bash
git add integration/hooks/sdd-guard.sh
git commit -m "feat(hooks): add worktree isolation guard to sdd-guard.sh"
```

---

### Task 2: Add worktree isolation check to `codex-sdd-guard.sh`

**Files:**
- Modify: `integration/hooks/codex-sdd-guard.sh`

The check must be inserted **after** `non_exempt` is computed and determined to be non-empty, and **before** the `tier`/`phase` read from state.json. Specifically after:

```bash
if [ -z "$non_exempt" ]; then
  if [ -z "$paths" ] && [ "$tool_name" = "Bash" ] && looks_like_write_bash; then
    print_context "SDD reminder: this Bash command appears to write files. If it edits source, ensure .sdd/state.json has tier set and phase is implement or verify."
  fi
  exit 0
fi
```

And before:
```bash
tier=""
phase=""
```

- [ ] **Step 1: Insert the worktree check**

Find and replace the exact string:
```bash
tier=""
phase=""
if [ -f "$state" ]; then
  tier="$(json_get "$state" "tier")"
  phase="$(json_get "$state" "phase")"
fi
```

With:
```bash
# Block source edits from the primary checkout; linked worktrees only.
if [ "${SDD_ALLOW_MAIN_WORKTREE:-}" != "1" ]; then
  _git_dir="$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P || true)"
  _git_common="$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P || true)"
  _superproject="$(git rev-parse --show-superproject-working-tree 2>/dev/null || true)"
  if [ -n "$_git_dir" ] && [ "$_git_dir" = "$_git_common" ] && [ -z "$_superproject" ]; then
    deny "SDD: source edits are only allowed from a linked git worktree. Create one with: git worktree add .worktrees/<branch> -b <branch>. For maintenance, set SDD_ALLOW_MAIN_WORKTREE=1."
    exit 0
  fi
fi

tier=""
phase=""
if [ -f "$state" ]; then
  tier="$(json_get "$state" "tier")"
  phase="$(json_get "$state" "phase")"
fi
```

Note: using `_git_dir` etc. to avoid shadowing any existing local variables.

- [ ] **Step 2: Syntax check**

```bash
bash -n integration/hooks/codex-sdd-guard.sh
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add integration/hooks/codex-sdd-guard.sh
git commit -m "feat(hooks): add worktree isolation guard to codex-sdd-guard.sh"
```

---

### Task 3: Create `integration/hooks/README.md`

**Files:**
- Create: `integration/hooks/README.md`

- [ ] **Step 1: Write the README**

Content:

```markdown
# SDD Hooks

Claude Code and Codex hook scripts that enforce SDD workflow rules locally.

## Files

| File | Platform | Type | Purpose |
|---|---|---|---|
| `sdd-guard.sh` | Claude Code | PreToolUse | Blocks source edits before spec is frozen; requires linked worktree |
| `skill-reminder.sh` | Claude Code | PostToolUse | Reminds which superpowers skill belongs to the current SDD phase |
| `codex-sdd-guard.sh` | Codex | PreToolUse | Same as sdd-guard.sh for Codex |
| `codex-skill-reminder.sh` | Codex | UserPromptSubmit | Same as skill-reminder.sh for Codex |

## Worktree requirement

These hooks block source edits when run from the **primary git checkout**.
All feature work must be done inside a **linked git worktree**:

```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
cd .worktrees/<branch-name>
```

Each worktree has its own `.sdd/` directory, so phase tracking is automatically isolated per feature.

### Why

A single `.sdd/state.json` in the primary checkout would conflict across parallel feature branches.
By requiring a linked worktree, phase state is per-branch by construction.

## Escape hatch

For maintenance work (updating hooks, debugging, one-off edits):

```bash
SDD_ALLOW_MAIN_WORKTREE=1 # set before running your tool
```

## Codex: trusting hooks after install

After copying hooks to your project's `.codex/` configuration,
Codex requires explicit trust. Run:

```
/hooks
```

inside a Codex session and confirm the hook files listed there.
Re-run `/hooks` whenever you update the hook scripts.

## Dependencies

- `jq` (preferred) or `python3` (fallback) — for JSON parsing
- `git` — for worktree detection

Both are checked and installed by `integration/update.sh` if missing.
```

- [ ] **Step 2: Verify file exists**

```bash
ls integration/hooks/README.md
```
Expected: file listed.

- [ ] **Step 3: Commit**

```bash
git add integration/hooks/README.md
git commit -m "docs(hooks): add README with worktree requirement and Codex trust steps"
```
