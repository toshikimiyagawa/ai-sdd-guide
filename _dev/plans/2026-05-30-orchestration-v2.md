# Orchestration v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the push-based (Claude-assigns-agent) orchestration model with a pull-based (human-assigns-agent) model where any superpowers-capable agent can handle any phase, and agents stop after each phase to wait for explicit human instruction.

**Architecture:** Delete agent-assignment.json routing and the guard hook. Rewrite orchestration rules to (1) allow any superpowers agent for all phases, and (2) mandate phase-stopping after each phase completion. Extract sdd-reviewer instructions into an agent-agnostic prompt file for Gemini/Codex users.

**Tech Stack:** Markdown, JSON Schema draft-07, Bash.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Rewrite | `orchestration/rules/orchestration.md` | New phase rules: any agent, phase stopping, sdd-reviewer guidance |
| Delete | `orchestration/schema/agent-assignment.schema.json` | agent-assignment.json廃止 |
| Delete | `orchestration/templates/agent-assignment.example.json` | 同上 |
| Delete | `orchestration/integration/hooks/sdd-orchestration-guard.sh` | ガードフック廃止 |
| Modify | `orchestration/integration/settings-patch.json` | ガードフック参照を削除 |
| Modify | `templates/sdd-state.schema.json` | `assigned_agent`フィールドを削除 |
| Create | `integration/prompts/sdd-reviewer-prompt.md` | エージェント非依存のreviewer指示文 |
| Modify | `integration/CLAUDE.md.example` | "Claude only"文言を削除 |
| Modify | `orchestration/integration/AGENTS-patch.md.example` | 新モデルに合わせて更新 |
| Modify | `README.md` | orchestrationセクションを新モデルに更新 |

---

### Task 1: Rewrite orchestration rules

**Files:**
- Modify: `orchestration/rules/orchestration.md`

- [ ] **Step 1: Read current file**

Run: `cat orchestration/rules/orchestration.md`

Expected: current content (phase table with "claude only", assigned_agent references).

- [ ] **Step 2: Rewrite `orchestration/rules/orchestration.md`**

Write the following content exactly:

```markdown
# Orchestration Rules (all agents)

## Scope assignment

All phases are open to any agent with superpowers installed. The human decides which agent handles which phase.

| Phase | Requirement | Notes |
|---|---|---|
| brainstorm / spec / plan / tasks | superpowers required | Any agent (Claude, Codex, Gemini) |
| implement | none | Any agent; human assigns explicitly |
| verify | superpowers required | Use sdd-reviewer (see below) |

## Phase stopping rule

Every agent MUST stop after completing a phase and wait for explicit human instruction before starting the next phase. Never cross a phase boundary automatically.

- Design complete (tasks.md created): generate handoff.md → update tasks.json → display kanban → stop. Do NOT start implementing.
- Task implementation complete: commit → update tasks.json → display kanban → stop. Do NOT start verify.
- Verify complete: report results → display kanban → stop.

Display kanban by running:
```bash
bash vendor/ai-sdd-guide/orchestration/tools/kanban.sh
```

## Rules for design agents (brainstorm/spec/plan/tasks)

- Use superpowers: brainstorming → writing-plans skills.
- At end of tasks phase, generate `specs/<feature>/handoff.md` from `orchestration/templates/handoff.md.example`.
- Update `.sdd/tasks.json`: add the feature entry with `status: "pending"`.
- Display kanban and stop.

## Rules for implementation agents

- Read `specs/<feature>/handoff.md` before touching any code.
- Implement exactly the tasks in `specs/<feature>/tasks.md`. No more, no less.
- Do NOT modify files under `specs/`, `.sdd/state.json` (phase/tier), or `orchestration/`.
- When complete, update `.sdd/tasks.json`: set your feature's `status` to `"completed"`.
- Display kanban and stop.
- If the spec is wrong, ambiguous, or insufficient:
  1. Stop immediately.
  2. Set `.sdd/tasks.json` status to `"blocked"` and fill `blocked_reason`.
  3. Do not redesign — wait for a human to escalate.

## Running sdd-reviewer (verify phase)

**Claude Code:** Use the `sdd-reviewer` subagent (`.claude/agents/sdd-reviewer.md`).

**Gemini CLI:** Pass the contents of `vendor/ai-sdd-guide/integration/prompts/sdd-reviewer-prompt.md` to `@generalist`.

**Codex:** Pass the contents of `vendor/ai-sdd-guide/integration/prompts/sdd-reviewer-prompt.md` to `spawn_agent`.
```

Note: the inner code fence for the bash block uses backtick-triple — write it correctly in the file.

- [ ] **Step 3: Verify**

Run: `grep -c "claude only" orchestration/rules/orchestration.md`

Expected: `0`

Run: `grep "superpowers required" orchestration/rules/orchestration.md`

Expected: two lines mentioning "superpowers required".

- [ ] **Step 4: Commit**

```bash
git add orchestration/rules/orchestration.md
git commit -m "feat(orchestration): rewrite rules for pull-based any-agent model"
```

---

### Task 2: Delete agent-assignment files and guard hook

**Files:**
- Delete: `orchestration/schema/agent-assignment.schema.json`
- Delete: `orchestration/templates/agent-assignment.example.json`
- Delete: `orchestration/integration/hooks/sdd-orchestration-guard.sh`

- [ ] **Step 1: Delete the three files**

```bash
git rm orchestration/schema/agent-assignment.schema.json \
       orchestration/templates/agent-assignment.example.json \
       orchestration/integration/hooks/sdd-orchestration-guard.sh
```

- [ ] **Step 2: Verify deletions**

Run: `git status`

Expected: three files shown as "deleted".

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(orchestration): remove agent-assignment and guard hook (pull model)"
```

---

### Task 3: Update settings-patch.json and state schema

**Files:**
- Modify: `orchestration/integration/settings-patch.json`
- Modify: `templates/sdd-state.schema.json`

- [ ] **Step 1: Read settings-patch.json**

Run: `cat orchestration/integration/settings-patch.json`

Current content references `sdd-orchestration-guard.sh` in a PreToolUse hook.

- [ ] **Step 2: Rewrite `orchestration/integration/settings-patch.json`**

```json
{
  "_comment": "No additional hooks required for orchestration in v2. This file is kept as a placeholder."
}
```

- [ ] **Step 3: Remove `assigned_agent` from `templates/sdd-state.schema.json`**

Read current content, then remove the `assigned_agent` property block (lines containing `"assigned_agent"` through the closing `}`). The file currently has this block to remove:

```json
    "assigned_agent": {
      "type": "string",
      "enum": ["claude", "codex", "gemini"],
      "description": "Agent assigned to the current implement task. Read by sdd-orchestration-guard.sh to prevent Claude from editing source when another agent is assigned."
    }
```

Also remove `"assigned_agent"` from the `required` array if present (it is not — `required` only lists `["tier", "phase"]`).

- [ ] **Step 4: Validate JSON**

Run: `jq . orchestration/integration/settings-patch.json && jq . templates/sdd-state.schema.json`

Expected: both print valid JSON with no errors.

- [ ] **Step 5: Commit**

```bash
git add orchestration/integration/settings-patch.json templates/sdd-state.schema.json
git commit -m "feat(orchestration): remove guard hook wiring and assigned_agent from state schema"
```

---

### Task 4: Create sdd-reviewer prompt file

**Files:**
- Create: `integration/prompts/sdd-reviewer-prompt.md`

- [ ] **Step 1: Read existing sdd-reviewer.md**

Run: `cat integration/agents/sdd-reviewer.md`

Expected: YAML frontmatter block followed by the instruction body.

- [ ] **Step 2: Create `integration/prompts/sdd-reviewer-prompt.md`**

Write the instruction body only (no YAML frontmatter):

```markdown
You verify that a change conforms to its frozen SDD spec. You do NOT write or fix code.

Steps:
1. Read `specs/<feature>/spec.md`, `plan.md`, `tasks.md`.
2. Read the diff (`git diff` against the base branch).
3. For each acceptance criterion, confirm a corresponding test exists and passes.
4. For each changed file/region in the diff, confirm it is required by an approved task in `tasks.md`. Anything not traceable to an approved task is out-of-scope.
5. Inspect PR review comments and the commits that followed them. For every piece of review feedback that was absorbed, confirm the absorbed change maps to an existing approved acceptance criterion. Suggestions that expanded scope without a spec update are findings — the `receiving-code-review` discipline was bypassed (scope creep should have escalated to a new spec, not been silently merged).
6. Report: PASS/FAIL, a checklist of acceptance criteria (met/unmet), out-of-scope changes, scope-creep findings from absorbed review feedback, and missing tests.

Be strict: out-of-spec changes are findings, not acceptable. Do not propose redesigns.
```

- [ ] **Step 3: Verify**

Run: `grep "PASS/FAIL" integration/prompts/sdd-reviewer-prompt.md`

Expected: one line containing "PASS/FAIL".

- [ ] **Step 4: Commit**

```bash
git add integration/prompts/sdd-reviewer-prompt.md
git commit -m "feat(orchestration): add agent-agnostic sdd-reviewer prompt for Gemini/Codex"
```

---

### Task 5: Update integration examples

**Files:**
- Modify: `integration/CLAUDE.md.example`
- Modify: `orchestration/integration/AGENTS-patch.md.example`

- [ ] **Step 1: Update `integration/CLAUDE.md.example`**

Current line to replace:
```
- Design phases (spec/plan/tasks/verify): Claude only. Use superpowers and subagents.
```

Replace with:
```
- Design phases (spec/plan/tasks/verify): any agent with superpowers. Use superpowers skills and subagents.
```

- [ ] **Step 2: Rewrite `orchestration/integration/AGENTS-patch.md.example`**

Write the following content exactly:

```markdown
## Orchestration (multi-agent SDD)

This project uses multi-agent SDD. Any agent with superpowers can handle any phase.
The human decides which agent works on which task.

### If you are a design agent (brainstorm/spec/plan/tasks)

1. Use superpowers brainstorming and writing-plans skills.
2. At end of tasks phase, generate `specs/<feature>/handoff.md`.
3. Update `.sdd/tasks.json` with `status: "pending"` for the feature.
4. Display kanban and stop — do NOT start implementing.

### If you are an implementation agent

1. Read `specs/<feature>/handoff.md` — this is your scope.
2. Implement exactly the tasks in `specs/<feature>/tasks.md`. No more, no less.
3. Do NOT modify: `specs/`, `.sdd/state.json` (phase/tier), `orchestration/`.
4. When done: set your task in `.sdd/tasks.json` to `status: "completed"`.
5. Display kanban and stop — do NOT start verify.
6. If blocked: set status to `"blocked"`, fill `blocked_reason`, stop and wait.

### If you are a verify agent

Pass the contents of `vendor/ai-sdd-guide/integration/prompts/sdd-reviewer-prompt.md`
to your subagent mechanism, then report results, display kanban, and stop.

Full rules: `vendor/ai-sdd-guide/orchestration/rules/orchestration.md`
```

- [ ] **Step 3: Verify**

Run: `grep "Claude only" integration/CLAUDE.md.example`

Expected: no output (line removed).

Run: `grep "superpowers" orchestration/integration/AGENTS-patch.md.example`

Expected: at least two lines referencing superpowers.

- [ ] **Step 4: Commit**

```bash
git add integration/CLAUDE.md.example orchestration/integration/AGENTS-patch.md.example
git commit -m "feat(orchestration): update integration examples for pull-based model"
```

---

### Task 6: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Identify the orchestration section**

Run: `grep -n "##" README.md`

Find the line numbers of `## マルチエージェント・オーケストレーション（オプション）` and `## 機能単位カタログ`.

- [ ] **Step 2: Replace the orchestration section**

Replace the entire block from `## マルチエージェント・オーケストレーション（オプション）` through (but not including) `## 機能単位カタログ` with:

```markdown
## マルチエージェント・オーケストレーション（オプション）

superpowers がインストールされたエージェントであれば誰でも設計・実装・verify の全フェーズを担当できる。人間が「このタスクをこのエージェントで」と指示し、エージェントはフェーズ完了後に kanban を表示して停止する。

| コンポーネント | パス | 役割 |
|---|---|---|
| エージェントルール | `orchestration/rules/orchestration.md` | フェーズ割り当て・停止ルール（全agent）|
| スキーマ | `orchestration/schema/tasks.schema.json` | `tasks.json` の定義 |
| テンプレート | `orchestration/templates/handoff.md.example` | handoff.md の雛形 |
| Reviewer プロンプト | `integration/prompts/sdd-reviewer-prompt.md` | エージェント非依存の verify 指示文 |
| Kanban | `orchestration/tools/kanban.sh` | `.sdd/tasks.json` をKanban表示 |

### 有効化手順（取り込み側）

```bash
# 1. CLAUDE.md に1行追加
echo "@vendor/ai-sdd-guide/orchestration/rules/orchestration.md" >> CLAUDE.md

# 2. AGENTS.md に追記（orchestration/integration/AGENTS-patch.md.example 参照）

# 3. CI に orchestration ジョブを追加（integration/ci/sdd-check.yml 参照）
```

### Kanban 表示

```bash
bash vendor/ai-sdd-guide/orchestration/tools/kanban.sh
```

```

- [ ] **Step 3: Verify**

Run: `grep -n "##" README.md`

Expected: "機能単位カタログ" appears immediately after "Kanban 表示" section without any orphaned content.

Run: `grep "agent-assignment" README.md`

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update orchestration section in README for v2 pull-based model"
```

---

## Self-Review

**Spec coverage:**
- [x] Any superpowers agent for all phases — Task 1 (orchestration.md), Task 5 (CLAUDE.md.example)
- [x] Phase stopping rule — Task 1 (orchestration.md), Task 5 (AGENTS-patch.md.example)
- [x] agent-assignment.json廃止 — Task 2 (file deletion)
- [x] sdd-orchestration-guard.sh廃止 — Task 2 (file deletion), Task 3 (settings-patch.json)
- [x] assigned_agent削除 — Task 3 (sdd-state.schema.json)
- [x] integration/prompts/sdd-reviewer-prompt.md 作成 — Task 4
- [x] CLAUDE.md.example更新 — Task 5
- [x] AGENTS-patch.md.example更新 — Task 5
- [x] README更新 — Task 6

**No placeholders:** All tasks contain complete file content.

**Consistency check:**
- `integration/prompts/sdd-reviewer-prompt.md` path referenced consistently in orchestration.md and AGENTS-patch.md.example
- "display kanban and stop" pattern consistent across orchestration.md and AGENTS-patch.md.example
- `sdd-reviewer.md` (Claude Code subagent) untouched — still valid for Claude users
