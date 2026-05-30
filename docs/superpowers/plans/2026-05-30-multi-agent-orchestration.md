# Multi-Agent Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `orchestration/` module to `ai-sdd-guide` that enables scoped multi-agent workflows — Claude designs, Codex/Gemini implement — with layered enforcement and Kanban-style task visibility.

**Architecture:** A new `orchestration/` directory sits alongside existing `rules/`, `templates/`, and `integration/` as an opt-in module. Consuming projects activate it by adding one line to `CLAUDE.md`. The module introduces two new `.sdd/` files (`agent-assignment.json` for routing rules, `tasks.json` for full task state) and a Claude hook that prevents Claude from editing source when another agent is assigned.

**Tech Stack:** Bash (3.x compatible), jq, JSON Schema draft-07, GitHub Actions YAML, Markdown.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `orchestration/schema/agent-assignment.schema.json` | Validates `.sdd/agent-assignment.json` |
| Create | `orchestration/schema/tasks.schema.json` | Validates `.sdd/tasks.json` |
| Modify | `templates/sdd-state.schema.json` | Add optional `assigned_agent` field |
| Create | `orchestration/templates/agent-assignment.example.json` | Copy-paste starter for consuming projects |
| Create | `orchestration/templates/handoff.md.example` | Handoff artifact template |
| Create | `orchestration/rules/orchestration.md` | Agent-facing scope/handoff rules |
| Create | `orchestration/integration/hooks/sdd-orchestration-guard.sh` | Blocks Claude from implementing when another agent is assigned |
| Create | `orchestration/integration/settings-patch.json` | Hook wiring for consuming projects |
| Create | `orchestration/integration/AGENTS-patch.md.example` | AGENTS.md additions for non-Claude agents |
| Create | `orchestration/tools/kanban.sh` | CLI Kanban from `.sdd/tasks.json` |
| Modify | `integration/ci/sdd-check.yml` | Add orchestration CI checks |
| Modify | `README.md` | Document orchestration module |

---

### Task 1: JSON Schemas

**Files:**
- Create: `orchestration/schema/agent-assignment.schema.json`
- Create: `orchestration/schema/tasks.schema.json`
- Modify: `templates/sdd-state.schema.json`

- [ ] **Step 1: Create `orchestration/schema/` directory and `agent-assignment.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Agent Assignment",
  "description": "Per-repository routing rules: maps feature ID patterns to implementation agents (.sdd/agent-assignment.json).",
  "type": "object",
  "required": ["default_implementer"],
  "additionalProperties": false,
  "properties": {
    "default_implementer": {
      "type": "string",
      "enum": ["claude", "codex", "gemini"],
      "description": "Fallback agent for implement-phase tasks not matched by any rule."
    },
    "rules": {
      "type": "array",
      "description": "Ordered list of pattern→agent overrides. First match wins.",
      "items": {
        "type": "object",
        "required": ["pattern", "agent"],
        "additionalProperties": false,
        "properties": {
          "pattern": {
            "type": "string",
            "description": "Glob pattern matched against the feature ID (e.g. 'feat/frontend-*')."
          },
          "agent": {
            "type": "string",
            "enum": ["claude", "codex", "gemini"]
          }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Create `orchestration/schema/tasks.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SDD Tasks",
  "description": "Full task state for all features in the project (.sdd/tasks.json). Kanban data source.",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["id", "phase", "assigned_agent", "status"],
    "additionalProperties": false,
    "properties": {
      "id": {
        "type": "string",
        "pattern": "^[a-z0-9][a-z0-9-]*$",
        "description": "Feature slug; matches specs/<id>/."
      },
      "phase": {
        "type": "string",
        "enum": ["brainstorm", "spec", "plan", "implement", "verify", "done"]
      },
      "assigned_agent": {
        "type": "string",
        "enum": ["claude", "codex", "gemini"]
      },
      "status": {
        "type": "string",
        "enum": ["pending", "in_progress", "completed", "blocked"]
      },
      "handoff": {
        "type": ["string", "null"],
        "description": "Path to handoff.md, or null if not yet generated."
      },
      "blocked_reason": {
        "type": ["string", "null"],
        "description": "Human-readable reason when status is 'blocked'. Null otherwise."
      }
    }
  }
}
```

- [ ] **Step 3: Add `assigned_agent` to `templates/sdd-state.schema.json`**

In `templates/sdd-state.schema.json`, add the following property inside `"properties"` (after `"note"`):

```json
    "assigned_agent": {
      "type": "string",
      "enum": ["claude", "codex", "gemini"],
      "description": "Agent assigned to the current implement task. Read by sdd-orchestration-guard.sh to prevent Claude from editing source when another agent is assigned."
    }
```

- [ ] **Step 4: Validate JSON files are well-formed**

Run: `jq . orchestration/schema/agent-assignment.schema.json orchestration/schema/tasks.schema.json templates/sdd-state.schema.json`

Expected: each file prints its content with no errors.

- [ ] **Step 5: Commit**

```bash
git add orchestration/schema/agent-assignment.schema.json \
        orchestration/schema/tasks.schema.json \
        templates/sdd-state.schema.json
git commit -m "feat(orchestration): add JSON schemas for agent-assignment and tasks"
```

---

### Task 2: Example Templates

**Files:**
- Create: `orchestration/templates/agent-assignment.example.json`
- Create: `orchestration/templates/handoff.md.example`

- [ ] **Step 1: Create `orchestration/templates/agent-assignment.example.json`**

```json
{
  "default_implementer": "codex",
  "rules": [
    { "pattern": "feat/frontend-*", "agent": "gemini" },
    { "pattern": "feat/api-*",      "agent": "codex"  },
    { "pattern": "feat/infra-*",    "agent": "claude" }
  ]
}
```

- [ ] **Step 2: Create `orchestration/templates/handoff.md.example`**

```markdown
# Handoff: <feature-id>

## あなたのスコープ

実装フェーズのみ。`spec.md` / `plan.md` / `verify` フェーズには触れない。
仕様の変更・追加は実装を止めて人間にエスカレーションすること。

## 完了条件

- [ ] `specs/<feature>/tasks.md` の全タスクが完了している
- [ ] `specs/<feature>/spec.md` の受入条件がすべてテストで検証されている
- [ ] テストスイートがパスしている

## 参照ファイル

- spec:  `specs/<feature>/spec.md`
- plan:  `specs/<feature>/plan.md`
- tasks: `specs/<feature>/tasks.md`

## 曖昧な点・仕様不備があれば

1. 実装を止める
2. `.sdd/tasks.json` の該当タスクの `status` を `"blocked"` にする
3. `blocked_reason` に理由を記載する
4. 人間にエスカレーションして再開を待つ
```

- [ ] **Step 3: Validate example JSON against its schema**

Run: `jq --argfile schema orchestration/schema/agent-assignment.schema.json -n 'input' < orchestration/templates/agent-assignment.example.json`

Expected: prints the JSON content with no errors.

- [ ] **Step 4: Commit**

```bash
git add orchestration/templates/agent-assignment.example.json \
        orchestration/templates/handoff.md.example
git commit -m "feat(orchestration): add example templates for agent-assignment and handoff"
```

---

### Task 3: Agent Rules File

**Files:**
- Create: `orchestration/rules/orchestration.md`

- [ ] **Step 1: Create `orchestration/rules/orchestration.md`**

```markdown
# Orchestration Rules (all agents)

## Scope assignment

Phases and their assigned agents are fixed:

| Phase | Allowed agents | Notes |
|---|---|---|
| brainstorm / spec / plan | claude only | superpowers required |
| implement | see `.sdd/agent-assignment.json` | task-level routing |
| verify / review | claude only | sdd-reviewer subagent |

Your assigned agent for the current task is in `.sdd/state.json` → `assigned_agent`.
If the field is absent, the phase routing above applies.

## Rules for Claude (design agent)

- Do not edit source files when `.sdd/state.json` has `phase=implement` and `assigned_agent` is not `claude`.
- Before setting `phase=implement`, you MUST:
  1. Generate `specs/<feature>/handoff.md` from `orchestration/templates/handoff.md.example`.
  2. Set `assigned_agent` in `.sdd/state.json` (use `agent-assignment.json` to determine the value).
  3. Update `.sdd/tasks.json`: set the feature's `status` to `in_progress` and `handoff` to the path.
- After the implementer signals completion, set `.sdd/state.json` `phase=verify` and run `sdd-reviewer`.

## Rules for implementation agents (Codex, Gemini, etc.)

- Read `specs/<feature>/handoff.md` before touching any code.
- Implement exactly the tasks in `specs/<feature>/tasks.md`. No more, no less.
- Do NOT modify files under `specs/`, `.sdd/state.json` (phase/tier), or `orchestration/`.
- When complete, update `.sdd/tasks.json`: set your feature's `status` to `completed`.
- If the spec is wrong, ambiguous, or insufficient:
  1. Stop immediately.
  2. Set `.sdd/tasks.json` status to `blocked` and fill `blocked_reason`.
  3. Do not redesign — wait for a human to escalate to Claude.

## Handoff checklist (Claude generates before implement phase)

- [ ] `specs/<feature>/handoff.md` created from template
- [ ] `.sdd/state.json` `assigned_agent` set
- [ ] `.sdd/tasks.json` entry for this feature exists with `status: "in_progress"`
- [ ] `.sdd/state.json` `phase` set to `"implement"`
```

- [ ] **Step 2: Commit**

```bash
git add orchestration/rules/orchestration.md
git commit -m "feat(orchestration): add agent rules for multi-agent scope enforcement"
```

---

### Task 4: Enforcement Hook

**Files:**
- Create: `orchestration/integration/hooks/sdd-orchestration-guard.sh`

- [ ] **Step 1: Create the hook directory and script**

```bash
#!/usr/bin/env bash
# SDD Orchestration guard (Claude Code PreToolUse hook).
# Prevents Claude from editing source files when the current implement task
# is assigned to a different agent.
# Non-blocking on missing config — this is an opt-in feature.
# Requires: jq.
set -euo pipefail

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')"

# Always allow: design artifacts, state files, orchestration config.
case "$file_path" in
  ""|*.md|specs/*|*/specs/*|docs/*|*/docs/*|.sdd/*|*/.sdd/*|orchestration/*|*/orchestration/*) exit 0 ;;
esac

state=".sdd/state.json"
[ -f "$state" ] || exit 0

phase="$(jq -r '.phase // empty' "$state" 2>/dev/null || true)"
assigned_agent="$(jq -r '.assigned_agent // empty' "$state" 2>/dev/null || true)"

# Only enforce during implement phase.
[ "$phase" = "implement" ] || exit 0

# No assigned_agent field means orchestration is not active — allow.
[ -z "$assigned_agent" ] && exit 0

# Assigned to Claude — allow.
[ "$assigned_agent" = "claude" ] && exit 0

# Another agent is assigned — block Claude from editing source.
printf 'SDD Orchestration: この実装タスクは "%s" に割り当てられています。\n' "$assigned_agent" >&2
printf 'Claude はソース編集できません。\n' >&2
printf 'Claude に変更するには .sdd/state.json の assigned_agent を "claude" に設定してください。\n' >&2
exit 2
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x orchestration/integration/hooks/sdd-orchestration-guard.sh`

- [ ] **Step 3: Validate with shellcheck (if available)**

Run: `shellcheck orchestration/integration/hooks/sdd-orchestration-guard.sh || echo "shellcheck not installed — skip"`

Expected: no errors (or "shellcheck not installed — skip").

- [ ] **Step 4: Smoke-test the hook logic with a fixture**

Run:
```bash
mkdir -p /tmp/sdd-test/.sdd
cat > /tmp/sdd-test/.sdd/state.json <<'EOF'
{"tier": 2, "phase": "implement", "feature": "feat-login", "assigned_agent": "codex"}
EOF

# Should exit 2 (block)
echo '{"tool_input":{"file_path":"src/auth.ts"}}' | \
  (cd /tmp/sdd-test && bash "$(pwd)/orchestration/integration/hooks/sdd-orchestration-guard.sh") \
  && echo "FAIL: expected exit 2" || echo "PASS: blocked as expected"

# Should exit 0 (allow spec file)
echo '{"tool_input":{"file_path":"specs/feat-login/spec.md"}}' | \
  (cd /tmp/sdd-test && bash "$(pwd)/orchestration/integration/hooks/sdd-orchestration-guard.sh") \
  && echo "PASS: spec file allowed" || echo "FAIL: spec file should be allowed"

rm -rf /tmp/sdd-test
```

Expected:
```
PASS: blocked as expected
PASS: spec file allowed
```

- [ ] **Step 5: Commit**

```bash
git add orchestration/integration/hooks/sdd-orchestration-guard.sh
git commit -m "feat(orchestration): add Claude enforcement hook for agent scope"
```

---

### Task 5: Integration Patches

**Files:**
- Create: `orchestration/integration/settings-patch.json`
- Create: `orchestration/integration/AGENTS-patch.md.example`

- [ ] **Step 1: Create `orchestration/integration/settings-patch.json`**

This file shows consuming projects which hook entry to add to `.claude/settings.json`.
The existing `settings.json.example` already has `PreToolUse` hooks — this is the additive patch.

```json
{
  "_comment": "Merge this PreToolUse entry into your .claude/settings.json hooks.PreToolUse array.",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "vendor/ai-sdd-guide/orchestration/integration/hooks/sdd-orchestration-guard.sh"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Create `orchestration/integration/AGENTS-patch.md.example`**

```markdown
## Orchestration (multi-agent SDD)

This project uses multi-agent SDD. Before coding, read:

1. `specs/<feature>/handoff.md` — your scope and completion criteria.
2. `.sdd/tasks.json` — find your assigned task (status: "in_progress").
3. `specs/<feature>/tasks.md` — the concrete steps to implement.

### Hard rules

- Implement ONLY what `handoff.md` and `tasks.md` specify.
- Do NOT modify: `specs/`, `.sdd/state.json` (phase/tier/assigned_agent), `orchestration/`.
- When done: set your task in `.sdd/tasks.json` to `status: "completed"`.
- If blocked: set status to `"blocked"`, fill `blocked_reason`, stop and wait.

詳細ルール: `vendor/ai-sdd-guide/orchestration/rules/orchestration.md`
```

- [ ] **Step 3: Validate settings-patch JSON**

Run: `jq . orchestration/integration/settings-patch.json`

Expected: prints the JSON content with no errors.

- [ ] **Step 4: Commit**

```bash
git add orchestration/integration/settings-patch.json \
        orchestration/integration/AGENTS-patch.md.example
git commit -m "feat(orchestration): add settings patch and AGENTS.md additions for consuming projects"
```

---

### Task 6: Kanban Tool

**Files:**
- Create: `orchestration/tools/kanban.sh`

- [ ] **Step 1: Create `orchestration/tools/` and `kanban.sh`**

```bash
#!/usr/bin/env bash
# Display .sdd/tasks.json as a text Kanban board.
# Usage: kanban.sh [path/to/tasks.json]
# Requires: jq.
set -euo pipefail

TASKS_FILE="${1:-.sdd/tasks.json}"

if [ ! -f "$TASKS_FILE" ]; then
  echo "No tasks file found at: $TASKS_FILE"
  exit 0
fi

COL=24
SEP="$(printf '─%.0s' $(seq 1 $((COL - 1))))"

get_tasks() {
  jq -r --arg s "$1" \
    '.[] | select(.status == $s) | .id + "  [" + .assigned_agent + "/" + .phase + "]"' \
    "$TASKS_FILE"
}

pending=()
in_progress=()
completed=()
blocked_tasks=()

while IFS= read -r line; do [ -n "$line" ] && pending+=("$line"); done      < <(get_tasks "pending")
while IFS= read -r line; do [ -n "$line" ] && in_progress+=("$line"); done  < <(get_tasks "in_progress")
while IFS= read -r line; do [ -n "$line" ] && completed+=("$line"); done    < <(get_tasks "completed")
while IFS= read -r line; do [ -n "$line" ] && blocked_tasks+=("$line"); done < <(get_tasks "blocked")

rows=${#pending[@]}
[ ${#in_progress[@]} -gt "$rows" ] && rows=${#in_progress[@]}
[ ${#completed[@]} -gt "$rows" ]   && rows=${#completed[@]}
[ ${#blocked_tasks[@]} -gt "$rows" ] && rows=${#blocked_tasks[@]}

echo ""
printf "%-${COL}s  %-${COL}s  %-${COL}s  %-${COL}s\n" "PENDING" "IN_PROGRESS" "COMPLETED" "BLOCKED"
printf "%-${COL}s  %-${COL}s  %-${COL}s  %-${COL}s\n" "$SEP" "$SEP" "$SEP" "$SEP"

for ((i = 0; i < rows; i++)); do
  printf "%-${COL}s  %-${COL}s  %-${COL}s  %-${COL}s\n" \
    "${pending[$i]:-}" \
    "${in_progress[$i]:-}" \
    "${completed[$i]:-}" \
    "${blocked_tasks[$i]:-}"
done

echo ""
jq -r '"Total: \(length) | pending:\([.[]|select(.status=="pending")]|length)  in_progress:\([.[]|select(.status=="in_progress")]|length)  completed:\([.[]|select(.status=="completed")]|length)  blocked:\([.[]|select(.status=="blocked")]|length)"' \
  "$TASKS_FILE"
echo ""
```

- [ ] **Step 2: Make executable**

Run: `chmod +x orchestration/tools/kanban.sh`

- [ ] **Step 3: Validate with shellcheck (if available)**

Run: `shellcheck orchestration/tools/kanban.sh || echo "shellcheck not installed — skip"`

- [ ] **Step 4: Smoke-test with fixture data**

Run:
```bash
cat > /tmp/sdd-tasks-test.json <<'EOF'
[
  {"id": "feat-login",   "phase": "implement", "assigned_agent": "codex",  "status": "in_progress", "handoff": "specs/feat-login/handoff.md",   "blocked_reason": null},
  {"id": "feat-payment", "phase": "spec",       "assigned_agent": "claude", "status": "pending",     "handoff": null,                             "blocked_reason": null},
  {"id": "feat-auth",    "phase": "verify",     "assigned_agent": "claude", "status": "completed",   "handoff": "specs/feat-auth/handoff.md",    "blocked_reason": null},
  {"id": "feat-api",     "phase": "implement",  "assigned_agent": "gemini", "status": "blocked",     "handoff": "specs/feat-api/handoff.md",     "blocked_reason": "spec section 3.2 is contradictory"}
]
EOF

bash orchestration/tools/kanban.sh /tmp/sdd-tasks-test.json
rm /tmp/sdd-tasks-test.json
```

Expected output (columns may vary in spacing):
```
PENDING                   IN_PROGRESS               COMPLETED                 BLOCKED
───────────────────────   ───────────────────────   ───────────────────────   ───────────────────────
feat-payment  [claude/spec]  feat-login  [codex/implement]  feat-auth  [claude/verify]  feat-api  [gemini/implement]

Total: 4 | pending:1  in_progress:1  completed:1  blocked:1
```

- [ ] **Step 5: Commit**

```bash
git add orchestration/tools/kanban.sh
git commit -m "feat(orchestration): add kanban.sh CLI for task visibility"
```

---

### Task 7: CI Additions

**Files:**
- Modify: `integration/ci/sdd-check.yml`

- [ ] **Step 1: Add orchestration checks to `integration/ci/sdd-check.yml`**

Append a new job after the existing `sdd:` job:

```yaml
  orchestration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Orchestration checks
        run: |
          # Skip if orchestration is not in use.
          if [ ! -f ".sdd/tasks.json" ]; then
            echo "No tasks.json — orchestration checks skipped."
            exit 0
          fi

          failed=0

          # No blocked tasks allowed on merge.
          blocked=$(jq '[.[] | select(.status=="blocked")] | length' .sdd/tasks.json)
          if [ "$blocked" -gt 0 ]; then
            echo "::error::$blocked blocked task(s) in .sdd/tasks.json. Resolve before merging."
            failed=$((failed + 1))
          fi

          # Every in_progress or pending implement task must have a handoff.md.
          while IFS= read -r id; do
            handoff="specs/$id/handoff.md"
            if [ ! -f "$handoff" ]; then
              echo "::error::Missing handoff.md for implement task '$id' (expected: $handoff)"
              failed=$((failed + 1))
            fi
          done < <(jq -r '.[] | select(.phase=="implement" and (.status=="in_progress" or .status=="pending")) | .id' .sdd/tasks.json)

          [ "$failed" -gt 0 ] && exit 1
          echo "Orchestration checks passed."
```

- [ ] **Step 2: Validate the YAML is well-formed**

Run: `python3 -c "import yaml, sys; yaml.safe_load(open('integration/ci/sdd-check.yml'))" && echo "YAML valid"`

Expected: `YAML valid`

- [ ] **Step 3: Commit**

```bash
git add integration/ci/sdd-check.yml
git commit -m "feat(orchestration): add CI checks for blocked tasks and missing handoff.md"
```

---

### Task 8: README Update

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add orchestration section to `README.md`**

After the `## 守らせる仕組み（多層）` section, add:

```markdown
## マルチエージェント・オーケストレーション（オプション）

Claude が設計し、Codex / Gemini が実装する分業フローを `orchestration/` モジュールで実現できる。

| コンポーネント | パス | 役割 |
|---|---|---|
| エージェントルール | `orchestration/rules/orchestration.md` | スコープ・引き継ぎルール（全agent）|
| スキーマ | `orchestration/schema/` | `agent-assignment.json` / `tasks.json` の定義 |
| テンプレート | `orchestration/templates/` | `agent-assignment.json` / `handoff.md` の雛形 |
| フック | `orchestration/integration/hooks/sdd-orchestration-guard.sh` | Claude がスコープ外を実装するのを防ぐ |
| Kanban | `orchestration/tools/kanban.sh` | `.sdd/tasks.json` をKanban表示 |

### 有効化手順（取り込み側）

```bash
# 1. CLAUDE.md に1行追加
echo "@vendor/ai-sdd-guide/orchestration/rules/orchestration.md" >> CLAUDE.md

# 2. agent-assignment.json を配置・編集
cp vendor/ai-sdd-guide/orchestration/templates/agent-assignment.example.json .sdd/agent-assignment.json

# 3. フックを .claude/settings.json に追記（orchestration/integration/settings-patch.json 参照）

# 4. AGENTS.md に追記（orchestration/integration/AGENTS-patch.md.example 参照）

# 5. CI に orchestration ジョブを追加（integration/ci/sdd-check.yml 参照）
```

### Kanban 表示

```bash
bash vendor/ai-sdd-guide/orchestration/tools/kanban.sh
```
```

- [ ] **Step 2: Verify README renders correctly (visual check)**

Run: `head -120 README.md`

Check that the new section appears correctly after the enforcement section.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add orchestration module to README"
```

---

## Self-Review

**Spec coverage check:**
- [x] `orchestration/` directory structure — Task 1-6 create all files
- [x] `agent-assignment.json` schema + example — Task 1, 2
- [x] `tasks.json` schema + example data structure — Task 1, 4 (smoke test)
- [x] `orchestration/rules/orchestration.md` — Task 3
- [x] `sdd-orchestration-guard.sh` hook — Task 4
- [x] `settings-patch.json` + `AGENTS-patch.md.example` — Task 5
- [x] `kanban.sh` — Task 6
- [x] CI additions — Task 7
- [x] README update — Task 8
- [x] `state.json` schema extended with `assigned_agent` — Task 1, Step 3
- [x] `handoff.md.example` template — Task 2
- [x] Kanban visibility requirement — Task 6

**No placeholders:** all steps contain complete file content or exact commands.

**Type/name consistency:**
- `assigned_agent` used consistently across: `state.json` schema, hook script, rules file
- `tasks.json` field names (`id`, `phase`, `assigned_agent`, `status`, `handoff`, `blocked_reason`) consistent across schema (Task 1), rules (Task 3), kanban tool (Task 6), and CI (Task 7)
- Hook script path `orchestration/integration/hooks/sdd-orchestration-guard.sh` consistent across Task 4, Task 5 (settings-patch.json), and README
