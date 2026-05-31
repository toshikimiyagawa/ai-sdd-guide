# Parallel Feature Work and Freeze Stop Rule Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a STOP rule after Freeze to prevent same-session implementation starts, and document the feature-per-worktree pattern for parallel work.

**Architecture:** Documentation-only changes to two files. No schema, hook, or CI changes. Each task edits one file, verifies with grep, and commits.

**Tech Stack:** Markdown, Bash (grep for verification).

---

### Task 1: Update `rules/workflow.md` — STOP rule + parallel features section

**Files:**
- Modify: `rules/workflow.md:18` (Freeze step) and after Step 0 block

Current Freeze step (line 18):
```
4. Freeze — set `.sdd/state.json` `phase=implement`. This is the handoff gate to other agents.
```

Current Step 0 block ends at line 8 (before `## Design phases`).

- [ ] **Step 1: Read the file**

```bash
cat -n /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/rules/workflow.md
```

- [ ] **Step 2: Add STOP rule to the Freeze step**

Find and replace the Freeze step line:

old_string:
```
4. Freeze — set `.sdd/state.json` `phase=implement`. This is the handoff gate to other agents.
```

new_string:
```
4. Freeze — set `.sdd/state.json` `phase=implement`. This is the handoff gate to other agents.
   STOP. Do not begin implementation in the same session as freeze.
   Wait for an explicit instruction to implement before proceeding.
```

- [ ] **Step 3: Add parallel features section after the Tier exemptions block**

Append a new section at the end of the file (after the `## Tier exemptions` block):

```markdown

## Parallel features

To work on multiple features simultaneously, use a separate git worktree per feature.
Each worktree has its own `.sdd/` directory — state and phase tracking are automatically
isolated. Use the `superpowers:using-git-worktrees` skill to create the worktree.

Never share a single worktree across two features in progress at the same time.
```

- [ ] **Step 4: Verify**

```bash
grep -n "STOP\. Do not begin" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/rules/workflow.md
```
Expected: 1 match in the Freeze step.

```bash
grep -n "Parallel features" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/rules/workflow.md
```
Expected: 1 match as a section heading.

- [ ] **Step 5: Commit**

```bash
git -C /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide add rules/workflow.md
git -C /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide commit -m "fix(workflow): add freeze STOP rule and parallel feature worktree pattern"
```

---

### Task 2: Update `docs/01-workflow.md` — freeze STOP note + parallel work section

**Files:**
- Modify: `docs/01-workflow.md:21` (freeze step) and end of file

Current freeze step (line 21):
```
5. **freeze** — `.sdd/state.json` を `phase=implement` に。ここが他agentへの引き渡しゲート。
```

- [ ] **Step 1: Read the file**

```bash
cat -n /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/docs/01-workflow.md
```

- [ ] **Step 2: Add STOP note to the freeze step**

Find and replace the freeze line:

old_string:
```
5. **freeze** — `.sdd/state.json` を `phase=implement` に。ここが他agentへの引き渡しゲート。
```

new_string:
```
5. **freeze** — `.sdd/state.json` を `phase=implement` に。ここが他agentへの引き渡しゲート。
   **STOP：freeze と同一セッションで実装を開始してはいけない。人間から「実装して」と明示的に指示を受けてから実装フェーズに入ること。**
```

- [ ] **Step 3: Add parallel work section at the end of the file**

Append after the last line of the file:

```markdown

## 並列作業

複数の feature を同時に進める場合は、**feature ごとに git worktree を分ける**。
各 worktree が独立した `.sdd/` ディレクトリを持つため、`state.json` の衝突が起きない。

```bash
# worktree 作成（using-git-worktrees スキルで自動化も可）
git worktree add .worktrees/feature-b -b feat/feature-b
```

1つの worktree に複数の feature を混在させてはいけない。
```

- [ ] **Step 4: Verify**

```bash
grep -n "STOP：freeze" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/docs/01-workflow.md
```
Expected: 1 match in the freeze step.

```bash
grep -n "並列作業" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/docs/01-workflow.md
```
Expected: 1 match as a section heading.

- [ ] **Step 5: Commit**

```bash
git -C /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide add docs/01-workflow.md
git -C /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide commit -m "docs: add freeze STOP note and parallel work section to workflow guide"
```
