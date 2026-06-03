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
SDD_ALLOW_MAIN_WORKTREE=1 <tool>
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
