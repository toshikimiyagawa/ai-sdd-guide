# Make Orchestration and Catalog Modules Mandatory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove "optional" framing for orchestration and catalog modules and make them always-active in all consuming projects, with catalog auto-initializing via human conversation when `.sdd/catalog.json` is absent.

**Architecture:** Pure documentation changes across 5 files. No code, no tests. Each task edits one file, verifies with grep/cat, and commits. Tasks are independent and can be executed in any order.

**Tech Stack:** Markdown, Bash (grep for verification).

---

### Task 1: Update `integration/AGENTS.md.example` — add orchestration + catalog to rules list

**Files:**
- Modify: `integration/AGENTS.md.example:4-8`

Current "Read the canonical rules before any work:" block (lines 4–8):
```
Read the canonical rules before any work:
- `vendor/ai-sdd-guide/rules/core.md`
- `vendor/ai-sdd-guide/rules/workflow.md`
- `vendor/ai-sdd-guide/rules/subagents.md`
- `vendor/ai-sdd-guide/rules/conventions.md`
```

- [ ] **Step 1: Edit the file**

Replace the block above with:
```
Read the canonical rules before any work:
- `vendor/ai-sdd-guide/rules/core.md`
- `vendor/ai-sdd-guide/rules/workflow.md`
- `vendor/ai-sdd-guide/rules/subagents.md`
- `vendor/ai-sdd-guide/rules/conventions.md`
- `vendor/ai-sdd-guide/orchestration/rules/orchestration.md`
- `vendor/ai-sdd-guide/catalog/rules/catalog.md`
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -n "orchestration.md\|catalog.md" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/integration/AGENTS.md.example
```
Expected output (two lines, both under "Read before any work"):
```
6:- `vendor/ai-sdd-guide/orchestration/rules/orchestration.md`
7:- `vendor/ai-sdd-guide/catalog/rules/catalog.md`
```

- [ ] **Step 3: Commit**

```bash
git add integration/AGENTS.md.example
git commit -m "feat(integration): add orchestration and catalog rules to AGENTS.md.example"
```

---

### Task 2: Update `AGENTS.md` — add orchestration + catalog to rules list

**Files:**
- Modify: `AGENTS.md:3-7`

Current "Read before any work:" block (lines 3–7):
```
Read before any work:
- `rules/core.md`
- `rules/workflow.md`
- `rules/subagents.md`
- `rules/conventions.md`
```

- [ ] **Step 1: Edit the file**

Replace the block above with:
```
Read before any work:
- `rules/core.md`
- `rules/workflow.md`
- `rules/subagents.md`
- `rules/conventions.md`
- `orchestration/rules/orchestration.md`
- `catalog/rules/catalog.md`
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -n "orchestration/rules/orchestration.md\|catalog/rules/catalog.md" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/AGENTS.md
```
Expected output:
```
6:- `orchestration/rules/orchestration.md`
7:- `catalog/rules/catalog.md`
```

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "feat: add orchestration and catalog rules to AGENTS.md"
```

---

### Task 3: Update `catalog/rules/catalog.md` — initialization flow when `.sdd/catalog.json` is absent

**Files:**
- Modify: `catalog/rules/catalog.md:3-6`

Current "When to apply" section (lines 3–6):
```markdown
## When to apply

Only apply these rules when `.sdd/catalog.json` exists in the project root.
If the file is absent, skip all catalog steps entirely — the project does not use catalogs.
```

- [ ] **Step 1: Edit the file**

Replace the section above with:
```markdown
## When to apply

Always apply these rules. If `.sdd/catalog.json` is absent, initialize it first:

1. Ask the human: "Which catalog types should this project track? Examples: screens (SCR), apis (API), tables (TBL), jobs (JOB), events (EVT). Add any custom types you need."
2. Create `.sdd/catalog.json` with the chosen types, following this schema:
   ```json
   {
     "types": [
       { "id": "<type-id>", "label": "<表示名>", "id_prefix": "<PREFIX>" }
     ]
   }
   ```
   Reference schema: `vendor/ai-sdd-guide/catalog/schema/catalog.schema.json`
3. Commit with message: `chore: initialize sdd catalog`
4. Proceed with the normal catalog flow below.
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -n "skip all catalog steps\|Always apply\|initialize it first" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/catalog/rules/catalog.md
```
Expected: only the "Always apply" and "initialize it first" lines appear (no "skip all catalog steps" line).

- [ ] **Step 3: Commit**

```bash
git add catalog/rules/catalog.md
git commit -m "feat(catalog): initialize catalog via conversation instead of skipping when absent"
```

---

### Task 4: Update `README.md` — remove optional labels and activation steps, add table rows

**Files:**
- Modify: `README.md` (multiple locations)

- [ ] **Step 1: Add orchestration/ and catalog/ rows to the 構成 table (lines 12–18)**

Current 構成 table (lines 12–18):
```markdown
## 構成
| パス | 対象 | 言語 | 役割 |
|---|---|---|---|
| `rules/` | agent | 英語 | 常時参照する強制ルール（命令形・簡潔） |
| `docs/` | 人間 | 日本語 | 方法論の解説 |
| `templates/` | 両方 | - | spec / plan / tasks 雛形 |
| `integration/` | 取り込み側 | - | ルート入口・hooks・CI・subagent定義の見本 |
```

Replace with:
```markdown
## 構成
| パス | 対象 | 言語 | 役割 |
|---|---|---|---|
| `rules/` | agent | 英語 | 常時参照する強制ルール（命令形・簡潔） |
| `docs/` | 人間 | 日本語 | 方法論の解説 |
| `templates/` | 両方 | - | spec / plan / tasks 雛形 |
| `integration/` | 取り込み側 | - | ルート入口・hooks・CI・subagent定義の見本 |
| `orchestration/` | 両方 | - | マルチエージェント・オーケストレーション |
| `catalog/` | 両方 | - | 機能単位カタログ |
```

- [ ] **Step 2: Remove "(オプション)" from the orchestration heading (line 32)**

Current (line 32):
```
## マルチエージェント・オーケストレーション（オプション）
```

Replace with:
```
## マルチエージェント・オーケストレーション
```

- [ ] **Step 3: Delete the orchestration 有効化手順 section (lines 44–53)**

Current text to delete:
```markdown
### 有効化手順（取り込み側）

```bash
# 1. AGENTS.md に1行追加
echo "@vendor/ai-sdd-guide/orchestration/rules/orchestration.md" >> AGENTS.md

# 2. AGENTS.md に追記（orchestration/integration/AGENTS-patch.md.example 参照）

# 3. CI に orchestration ジョブを追加（integration/ci/sdd-check.yml 参照）
```

```
(Delete the entire `### 有効化手順（取り込み側）` block including the code fence and blank lines, leaving the `### Kanban 表示` section intact immediately after the orchestration description table.)

- [ ] **Step 4: Remove "(オプション)" from the catalog heading (line 61 after previous deletions)**

Current:
```
## 機能単位カタログ（オプション）
```

Replace with:
```
## 機能単位カタログ
```

- [ ] **Step 5: Delete the catalog 有効化手順 section and trailing sentence**

Current text to delete (the 有効化手順 block plus the sentence after it):
```markdown
### 有効化手順（取り込み側）

```bash
# 1. カタログ種類を宣言
cp vendor/ai-sdd-guide/catalog/templates/catalog.json.example .sdd/catalog.json
# → プロジェクトに合わせて types を編集

# 2. AGENTS.md に参照を追加
echo "@vendor/ai-sdd-guide/catalog/rules/catalog.md" >> AGENTS.md
```

有効化後は `spec.md` 作成時に、superpowers が使えるエージェントが `docs/design/` 配下にカタログと定義書を自動生成する。
```

(Delete the entire block. The `## 導入手順（取り込み側プロジェクト）` section that follows should remain intact.)

- [ ] **Step 6: Verify**

Run:
```bash
grep -n "オプション\|有効化手順" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/README.md
```
Expected: no output (zero matches).

Run:
```bash
grep -n "orchestration/\|catalog/" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/README.md | head -10
```
Expected: matches in the 構成 table and orchestration/catalog description sections.

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs: make orchestration and catalog mandatory, remove activation sections"
```

---

### Task 5: Update `docs/00-overview.md` — add orchestration/ and catalog/ to 全体像 table

**Files:**
- Modify: `docs/00-overview.md:21-26`

Current 全体像 table (lines 21–26):
```markdown
## 全体像
| 要素 | 対象 | 言語 | 役割 |
|---|---|---|---|
| `rules/` | agent | 英語 | 常時参照する強制ルール |
| `docs/` | 人間 | 日本語 | 方法論の解説 |
| `templates/` | 両方 | - | spec/plan/tasks 雛形 |
| `integration/` | 取り込み側 | - | ルート入口・hooks・CI・subagent定義 |
```

- [ ] **Step 1: Edit the file**

Replace the table with:
```markdown
## 全体像
| 要素 | 対象 | 言語 | 役割 |
|---|---|---|---|
| `rules/` | agent | 英語 | 常時参照する強制ルール |
| `docs/` | 人間 | 日本語 | 方法論の解説 |
| `templates/` | 両方 | - | spec/plan/tasks 雛形 |
| `integration/` | 取り込み側 | - | ルート入口・hooks・CI・subagent定義 |
| `orchestration/` | 両方 | - | マルチエージェント・オーケストレーション |
| `catalog/` | 両方 | - | 機能単位カタログ |
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -n "orchestration/\|catalog/" /Users/toshiki/ghq/github.com/toshikimiyagawa/ai-sdd-guide/docs/00-overview.md
```
Expected output:
```
28:| `orchestration/` | 両方 | - | マルチエージェント・オーケストレーション |
29:| `catalog/` | 両方 | - | 機能単位カタログ |
```
(Line numbers may differ slightly depending on exact table position.)

- [ ] **Step 3: Commit**

```bash
git add docs/00-overview.md
git commit -m "docs: add orchestration and catalog rows to overview table"
```
