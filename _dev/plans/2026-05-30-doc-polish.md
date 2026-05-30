# Doc Polish — Remove Claude-Only Language: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove "Claude のみ" / "Claude Code only" constraints from docs, replacing with "superpowers required, any agent" language, and translate remaining Japanese lines in agent-facing files to English.

**Architecture:** 9 targeted text edits across rules/, docs/, catalog/, and README.md. No structural changes. No file additions or deletions.

**Tech Stack:** Markdown only — no code, no tests, no schemas.

---

### Task 1: rules/core.md — DESIGN phases constraint

**Files:**
- Modify: `rules/core.md:6`

Current line 6:
```
- DESIGN phases (spec, plan, tasks, verify) — Claude Code only. Use superpowers + subagents + hooks.
```

- [ ] **Step 1: Edit rules/core.md**

Replace line 6 with:
```
- DESIGN phases (spec, plan, tasks, verify) — superpowers required, any agent. Use superpowers + subagents + hooks.
```

- [ ] **Step 2: Commit**

```bash
git add rules/core.md
git commit -m "docs(rules): remove Claude-only constraint from core.md"
```

---

### Task 2: rules/workflow.md — headings + Japanese line

**Files:**
- Modify: `rules/workflow.md:10,11,28,29,31`

Current lines:
- Line 10: `## Design phases (Claude only)`
- Line 11: `Drive these with superpowers skills (requires the superpowers plugin — Claude only).`
- Line 28: `## Verify phase (Claude)`
- Line 31: `- Create the PR. CI が設定されている場合は実行完了を待ち、全チェックが pass かつ mergeable であることを確認してから完了報告する。CI 結果を確認せずに完了を宣言してはならない。`

- [ ] **Step 1: Edit rules/workflow.md**

Replace line 10:
```
## Design phases (superpowers required)
```

Replace line 11:
```
Drive these with superpowers skills (requires the superpowers plugin).
```

Replace line 28:
```
## Verify phase (superpowers required)
```

Replace the Japanese line 31 with:
```
- Create the PR. If CI is configured, wait for completion and confirm all checks pass and the PR is mergeable before declaring completion. Never declare completion without verifying CI results.
```

- [ ] **Step 2: Commit**

```bash
git add rules/workflow.md
git commit -m "docs(rules): fix workflow.md headings and translate Japanese line"
```

---

### Task 3: rules/subagents.md — remove "design/verify only" from title

**Files:**
- Modify: `rules/subagents.md:1`

Current line 1:
```
# Subagent Rules (Claude — design/verify only)
```

- [ ] **Step 1: Edit rules/subagents.md**

Replace line 1 with:
```
# Subagent Rules (Claude Code)
```

Note: Agent tool / Task tool are Claude Code-specific mechanisms — keeping "Claude Code" in the title is correct. Only removing the "design/verify only" restriction phrasing.

- [ ] **Step 2: Commit**

```bash
git add rules/subagents.md
git commit -m "docs(rules): remove design/verify-only restriction from subagents.md title"
```

---

### Task 4: rules/conventions.md — translate Japanese line

**Files:**
- Modify: `rules/conventions.md:13`

Current line 13:
```
- PR のレビューは `sdd-reviewer` subagent に実施させる。人間のレビュー前に subagent が spec 適合を確認することで、レビュー負荷を下げる。
```

- [ ] **Step 1: Edit rules/conventions.md**

Replace line 13 with:
```
- Run `sdd-reviewer` before human review. The subagent confirms spec conformance first, reducing reviewer load.
```

- [ ] **Step 2: Commit**

```bash
git add rules/conventions.md
git commit -m "docs(rules): translate Japanese line in conventions.md to English"
```

---

### Task 5: docs/00-overview.md — "Claude のみ" in 中心思想

**Files:**
- Modify: `docs/00-overview.md:13-18`

Current lines 13-18:
```
## 中心思想：設計と実装の分離
- **設計（spec/plan/tasks/レビュー）= Claude のみ。** superpowers と subagent をフル活用して深く考える。
- **実装 = どのエージェントでも可。** 設計成果物 `specs/<feature>/` を唯一の契約として渡す。

この分離により、重い思考は Claude に集約しつつ、実装は Cursor / Copilot / Codex など
好きなツールで分担できる。そのため設計成果物には「設計の文脈を知らないエージェントでも
```

- [ ] **Step 1: Edit docs/00-overview.md**

Replace the 設計 bullet (line 14):
```
- **設計（spec/plan/tasks/レビュー）= superpowers 必須（どのエージェントでも可）。** superpowers と subagent をフル活用して深く考える。
```

Replace lines 17-18 (the explanation paragraph opening):
```
この分離により、設計フェーズは superpowers が使えるエージェントが担当し、実装は Cursor / Copilot / Codex など
好きなツールで分担できる。そのため設計成果物には「設計の文脈を知らないエージェントでも
```

- [ ] **Step 2: Commit**

```bash
git add docs/00-overview.md
git commit -m "docs: remove Claude-only language from 00-overview.md"
```

---

### Task 6: docs/01-workflow.md — section headings

**Files:**
- Modify: `docs/01-workflow.md:16,28`

Current:
- Line 16: `### 設計（Claudeのみ）`
- Line 28: `### 検証（Claude）`

- [ ] **Step 1: Edit docs/01-workflow.md**

Replace line 16:
```
### 設計（superpowers必須）
```

Replace line 28:
```
### 検証（superpowers必須）
```

- [ ] **Step 2: Commit**

```bash
git add docs/01-workflow.md
git commit -m "docs: fix workflow phase headings in 01-workflow.md"
```

---

### Task 7: docs/02-roles.md — Claude section + superpowers description

**Files:**
- Modify: `docs/02-roles.md:8-11,17,26-27`

Current lines 8-11:
```
## Claude（設計担当）
- brainstorm → spec → plan → tasks の作成。
- subagent と superpowers を使った深い検討。
- 実装後の検証（sdd-reviewer）。
```

Current line 17:
```
## subagent ロール（Claude・設計/検証のみ）
```

Current lines 26-27:
```
## superpowers（Claude Code 専用プラグイン）
設計フェーズで活用する。実装担当の他agentでは使えないため、成果物 `specs/<feature>/` に落とし込んで橋渡しする。
```

- [ ] **Step 1: Edit docs/02-roles.md**

Replace lines 8-11 (Claude section → 設計担当agent):
```
## 設計担当agent（superpowers必須）
- brainstorm → spec → plan → tasks の作成。
- subagent と superpowers を使った深い検討。
- 実装後の検証（sdd-reviewer）。
- Claude Code / Codex CLI / Gemini CLI いずれでも担当可。
```

Replace line 17:
```
## subagent ロール
```

Replace line 26:
```
## superpowers（Claude / Codex / Gemini 対応プラグイン）
```

Replace line 27:
```
設計・検証フェーズで活用する。Claude Code・Codex CLI・Gemini CLI でインストールして使える。成果物 `specs/<feature>/` に設計内容を落とし込み、superpowers を持たないagentへ橋渡しする。
```

- [ ] **Step 2: Commit**

```bash
git add docs/02-roles.md
git commit -m "docs: update roles and superpowers description in 02-roles.md"
```

---

### Task 8: README.md — 中心思想 + catalog description

**Files:**
- Modify: `README.md:9,64`

Current line 9:
```
- **設計 (spec/plan/tasks/レビュー) = Claude のみ**（superpowers + subagent + hooks をフル活用）
```

Current line 64:
```
Claude が spec 作成時（planned）と verify 完了時（confirmed）に自動更新する。
```

- [ ] **Step 1: Edit README.md**

Replace line 9:
```
- **設計 (spec/plan/tasks/レビュー) = superpowers 必須（どのエージェントでも可）**（superpowers + subagent + hooks をフル活用）
```

Replace line 64:
```
superpowers が使えるエージェントが spec 作成時（planned）と verify 完了時（confirmed）に自動更新する。
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: remove Claude-only language from README.md"
```

---

### Task 9: catalog/rules/catalog.md — remove "Claude" from title

**Files:**
- Modify: `catalog/rules/catalog.md:1`

Current line 1:
```
# Catalog Rules (Claude — spec/verify phases)
```

- [ ] **Step 1: Edit catalog/rules/catalog.md**

Replace line 1 with:
```
# Catalog Rules (spec/verify phases)
```

- [ ] **Step 2: Commit**

```bash
git add catalog/rules/catalog.md
git commit -m "docs(catalog): remove Claude-only label from catalog.md title"
```

---

### Final: Create PR

- [ ] **Step 1: Push branch and create PR**

```bash
git push -u origin refactor/remove-claude-only-language
gh pr create \
  --title "docs: remove Claude-only language, unify around superpowers capability" \
  --body "$(cat <<'EOF'
## Summary
- 設計・検証フェーズの制約を「Claude のみ」から「superpowers 必須（どのエージェントでも可）」に統一
- agent 向けファイル (rules/) に残っていた日本語行を英語化
- catalog.md / subagents.md タイトルの Claude 限定ニュアンスを削除

## Files changed
- `README.md`, `rules/core.md`, `rules/workflow.md`, `rules/subagents.md`, `rules/conventions.md`
- `docs/00-overview.md`, `docs/01-workflow.md`, `docs/02-roles.md`
- `catalog/rules/catalog.md`

## Test plan
- [ ] rules/ ファイルに日本語行が残っていないことを確認
- [ ] 「Claude のみ」「Claude Code only」表現が rules/ docs/ に残っていないことを確認
- [ ] subagents.md の Agent tool / Task tool 記述（Claude Code 固有）は維持されていることを確認

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
