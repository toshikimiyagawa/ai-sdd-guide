# CLAUDE.md → AGENTS.md Symlink Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make CLAUDE.md a symlink to AGENTS.md in both this repo and the integration templates, so all agents read a single unified file.

**Architecture:** Create AGENTS.md as the real file, delete CLAUDE.md and replace with `ln -s AGENTS.md CLAUDE.md`. Same pattern for integration templates. update.sh gains symlink creation logic; README.md setup instructions updated.

**Tech Stack:** Bash, git (symlink support via mode 120000), Markdown.

---

### Task 1: Create AGENTS.md and convert CLAUDE.md to symlink (this repo)

**Files:**
- Create: `AGENTS.md`
- Modify: `CLAUDE.md` (replace real file with symlink)

- [ ] **Step 1: Create AGENTS.md**

```bash
cat > /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/AGENTS.md << 'EOF'
# ai-sdd-guide — Agent Guidelines

Read before any work:
- `rules/core.md`
- `rules/workflow.md`
- `rules/subagents.md`
- `rules/conventions.md`

## superpowers save paths

Save design docs and plans to `_dev/` (not the default `docs/superpowers/`):
- Specs: `_dev/specs/YYYY-MM-DD-<topic>-design.md`
- Plans: `_dev/plans/YYYY-MM-DD-<feature-name>.md`

`_dev/` is this repository's own development history and is not intended for consuming projects.

## CLAUDE.md

CLAUDE.md is a symlink to this file. Do not replace it with a regular file.
EOF
```

- [ ] **Step 2: Replace CLAUDE.md with a symlink**

```bash
cd /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide
rm CLAUDE.md
ln -s AGENTS.md CLAUDE.md
```

- [ ] **Step 3: Verify symlink is correct**

```bash
ls -la CLAUDE.md
# Expected: CLAUDE.md -> AGENTS.md
cat CLAUDE.md
# Expected: shows AGENTS.md content
```

- [ ] **Step 4: Stage and verify git status**

```bash
git add AGENTS.md CLAUDE.md
git status
# Expected: new file: AGENTS.md
#           typechange: CLAUDE.md  (was regular file, now symlink)
```

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add AGENTS.md and convert CLAUDE.md to symlink"
```

---

### Task 2: Rewrite integration/AGENTS.md.example

**Files:**
- Modify: `integration/AGENTS.md.example`

- [ ] **Step 1: Overwrite with unified content**

```bash
cat > /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration/AGENTS.md.example << 'EOF'
# Project Guidelines

This project follows Spec-Driven Development (SDD).
Read the canonical rules before any work:
- `vendor/ai-sdd-guide/rules/core.md`
- `vendor/ai-sdd-guide/rules/workflow.md`
- `vendor/ai-sdd-guide/rules/subagents.md`
- `vendor/ai-sdd-guide/rules/conventions.md`

## Design phases (superpowers required)
Use superpowers skills (brainstorming → writing-plans) for spec/plan/tasks.
Capture output into `specs/<feature>/`. Human approves before freezing.

## Implementation phase (any agent)
Implement exactly the frozen `specs/<feature>/tasks.md`. No more, no less.
Every acceptance criterion must map to a passing test.
If the spec is wrong or insufficient: STOP and escalate. Do not redesign.

## Hard rules
- Do not modify files under `specs/` to fit an implementation.
- Do not expand scope beyond approved tasks.
- Do not disable SDD hooks or CI.

Human-facing docs: `vendor/ai-sdd-guide/docs/`
Templates: `vendor/ai-sdd-guide/templates/`
Hooks: `.claude/settings.json` (copy from `vendor/ai-sdd-guide/integration/settings.json.example`)
Subagents: `.claude/agents/` (copy from `vendor/ai-sdd-guide/integration/agents/`)

## CLAUDE.md
CLAUDE.md is a symlink to this file. Do not replace it with a regular file.

(If you change the submodule path, update all paths above to match.)
EOF
```

- [ ] **Step 2: Verify content**

```bash
cat /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration/AGENTS.md.example
# Expected: unified content with Design phases, Implementation phase, Hard rules sections
# No @vendor/... include lines
```

- [ ] **Step 3: Commit**

```bash
git add integration/AGENTS.md.example
git commit -m "feat(integration): rewrite AGENTS.md.example with unified plain-text content"
```

---

### Task 3: Convert integration/CLAUDE.md.example to symlink

**Files:**
- Modify: `integration/CLAUDE.md.example` (replace real file with symlink)

- [ ] **Step 1: Replace with symlink**

```bash
cd /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration
rm CLAUDE.md.example
ln -s AGENTS.md.example CLAUDE.md.example
```

- [ ] **Step 2: Verify**

```bash
ls -la /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration/CLAUDE.md.example
# Expected: CLAUDE.md.example -> AGENTS.md.example
cat /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration/CLAUDE.md.example
# Expected: shows AGENTS.md.example content (unified content, no @ includes)
```

- [ ] **Step 3: Stage and verify git status**

```bash
cd /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide
git add integration/CLAUDE.md.example
git status
# Expected: typechange: integration/CLAUDE.md.example
```

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(integration): convert CLAUDE.md.example to symlink → AGENTS.md.example"
```

---

### Task 4: Update integration/update.sh

**Files:**
- Modify: `integration/update.sh:26-29` (protected array) and end of file (new symlink block)

Current `protected` array (lines 26-30):
```bash
protected=(
  "CLAUDE.md:$INTEGRATION/CLAUDE.md.example"
  "AGENTS.md:$INTEGRATION/AGENTS.md.example"
  ".claude/settings.json:$INTEGRATION/settings.json.example"
)
```

- [ ] **Step 1: Remove CLAUDE.md from protected array**

Edit `integration/update.sh` to change the `protected` array from:
```bash
protected=(
  "CLAUDE.md:$INTEGRATION/CLAUDE.md.example"
  "AGENTS.md:$INTEGRATION/AGENTS.md.example"
  ".claude/settings.json:$INTEGRATION/settings.json.example"
)
```
to:
```bash
protected=(
  "AGENTS.md:$INTEGRATION/AGENTS.md.example"
  ".claude/settings.json:$INTEGRATION/settings.json.example"
)
```

- [ ] **Step 2: Add symlink block after the protected loop**

After the `done` line that closes the `for entry in "${protected[@]}"` loop (currently line 47), add:

```bash

# --- CLAUDE.md: must be a symlink to AGENTS.md ---

CLAUDE="$PROJECT/CLAUDE.md"
if [[ -L "$CLAUDE" ]]; then
  : # already a symlink — leave it
elif [[ ! -e "$CLAUDE" ]]; then
  ln -s AGENTS.md "$CLAUDE"
  log "created CLAUDE.md → AGENTS.md symlink"
else
  log "WARNING: CLAUDE.md exists but is not a symlink — run: rm CLAUDE.md && ln -s AGENTS.md CLAUDE.md"
fi
```

- [ ] **Step 3: Verify the script is valid bash**

```bash
bash -n /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration/update.sh
# Expected: no output (syntax OK)
```

- [ ] **Step 4: Smoke-test the script against a temp directory**

```bash
TMPDIR=$(mktemp -d)
# Simulate a git repo
git init "$TMPDIR"
bash /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration/update.sh "$TMPDIR"
ls -la "$TMPDIR/CLAUDE.md" "$TMPDIR/AGENTS.md"
# Expected:
# AGENTS.md  (regular file with unified content)
# CLAUDE.md -> AGENTS.md  (symlink)
rm -rf "$TMPDIR"
```

- [ ] **Step 5: Commit**

```bash
git add integration/update.sh
git commit -m "feat(integration): update.sh creates CLAUDE.md symlink instead of copying template"
```

---

### Task 5: Update README.md setup instructions

**Files:**
- Modify: `README.md` (setup step 2, currently lines 91-92)

Current step 2 block:
```bash
# 2. ルートに薄い入口を配置（一度だけコピー）
cp vendor/ai-sdd-guide/integration/CLAUDE.md.example ./CLAUDE.md
cp vendor/ai-sdd-guide/integration/AGENTS.md.example ./AGENTS.md
```

- [ ] **Step 1: Edit README.md step 2**

Replace the step 2 block with:
```bash
# 2. ルートに薄い入口を配置（一度だけコピー）
cp vendor/ai-sdd-guide/integration/AGENTS.md.example ./AGENTS.md
ln -s AGENTS.md CLAUDE.md        # CLAUDE.md は AGENTS.md のシンボリックリンクとして管理
```

- [ ] **Step 2: Verify README.md renders correctly**

```bash
grep -A 3 "ルートに薄い入口" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/README.md
# Expected: shows the updated 2-line block (cp AGENTS.md.example + ln -s)
# No cp CLAUDE.md.example line
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update setup instructions to create CLAUDE.md as symlink"
```
