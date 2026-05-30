# Catalog Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `catalog/` module to `ai-sdd-guide` that enables consuming projects to maintain system-wide design catalogs (screens, APIs, tables, etc.) automatically updated by Claude during spec and verify phases.

**Architecture:** A new `catalog/` directory provides schema, templates, and agent rules as an opt-in module. Consuming projects declare catalog types in `.sdd/catalog.json`; Claude reads this and updates `docs/design/<type>/index.md` and individual definition files at spec time (status: planned) and verify time (status: confirmed). One line added to `rules/workflow.md` integrates this into the normal SDD flow.

**Tech Stack:** JSON Schema draft-07, Markdown with YAML frontmatter.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `catalog/schema/catalog.schema.json` | Validates `.sdd/catalog.json` |
| Create | `catalog/templates/catalog.json.example` | Copy-paste starter for consuming projects |
| Create | `catalog/templates/index.md.example` | Catalog list template |
| Create | `catalog/templates/definition.md.example` | Individual definition template |
| Create | `catalog/rules/catalog.md` | Agent rules: when and how to update catalogs |
| Modify | `rules/workflow.md` | Add catalog reference line after Spec step |
| Modify | `README.md` | Document catalog module with activation steps |

---

### Task 1: JSON Schema

**Files:**
- Create: `catalog/schema/catalog.schema.json`

- [ ] **Step 1: Create `catalog/schema/catalog.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SDD Catalog",
  "description": "Declares the catalog types managed in this project (.sdd/catalog.json).",
  "type": "object",
  "required": ["types"],
  "additionalProperties": false,
  "properties": {
    "types": {
      "type": "array",
      "minItems": 1,
      "description": "Catalog types to maintain. Each type maps to a docs/design/<id>/ directory.",
      "items": {
        "type": "object",
        "required": ["id", "label", "id_prefix"],
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "string",
            "pattern": "^[a-z][a-z0-9-]*$",
            "description": "Directory name under docs/design/ (e.g. 'screens', 'apis', 'tables')."
          },
          "label": {
            "type": "string",
            "description": "Human-readable heading for index.md (e.g. '画面一覧')."
          },
          "id_prefix": {
            "type": "string",
            "pattern": "^[A-Z][A-Z0-9-]*$",
            "description": "Prefix for entry IDs (e.g. 'SCR', 'API', 'TBL'). Used as <id_prefix>-NNN."
          }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Validate JSON**

Run: `jq . catalog/schema/catalog.schema.json`

Expected: prints the JSON content with no errors.

- [ ] **Step 3: Commit**

```bash
git add catalog/schema/catalog.schema.json
git commit -m "feat(catalog): add JSON schema for catalog.json"
```

---

### Task 2: Templates

**Files:**
- Create: `catalog/templates/catalog.json.example`
- Create: `catalog/templates/index.md.example`
- Create: `catalog/templates/definition.md.example`

- [ ] **Step 1: Create `catalog/templates/catalog.json.example`**

```json
{
  "types": [
    { "id": "screens", "label": "画面一覧",    "id_prefix": "SCR" },
    { "id": "apis",    "label": "API一覧",      "id_prefix": "API" },
    { "id": "tables",  "label": "テーブル一覧", "id_prefix": "TBL" }
  ]
}
```

- [ ] **Step 2: Validate example against schema**

Run: `jq . catalog/templates/catalog.json.example`

Expected: prints the JSON with no errors.

- [ ] **Step 3: Create `catalog/templates/index.md.example`**

Write the following content exactly (no surrounding fences):

```
# <label>

<!-- catalog-type: <type-id> -->

| ID | 名称 | ステータス | feature | 定義書 |
|---|---|---|---|---|
| <PREFIX>-001 | <名称> | planned | [<feature-slug>](../../specs/<feature-slug>/spec.md) | [→](<PREFIX>-001-<slug>.md) |
```

- [ ] **Step 4: Create `catalog/templates/definition.md.example`**

Write the following content exactly (no surrounding fences):

```
---
id: <PREFIX>-001
title: <名称>
status: planned
feature: <feature-slug>
updated: YYYY-MM-DD
---

# <PREFIX>-001: <名称>

## 概要

（このエントリが表すものの1〜2行の説明）

## 仕様

（プロジェクトに合わせて自由に記述。
例：画面なら画面項目一覧、APIならリクエスト/レスポンス定義、テーブルならカラム定義）
```

- [ ] **Step 5: Commit**

```bash
git add catalog/templates/catalog.json.example \
        catalog/templates/index.md.example \
        catalog/templates/definition.md.example
git commit -m "feat(catalog): add example templates for catalog.json, index and definition"
```

---

### Task 3: Agent Rules File

**Files:**
- Create: `catalog/rules/catalog.md`

- [ ] **Step 1: Create `catalog/rules/catalog.md`**

Write the following content exactly (no surrounding fences):

```
# Catalog Rules (Claude — spec/verify phases)

## When to apply

Only apply these rules when `.sdd/catalog.json` exists in the project root.
If the file is absent, skip all catalog steps entirely — the project does not use catalogs.

## During spec phase — register as planned

When writing or updating `specs/<feature>/spec.md`, identify any new items that belong
in a catalog type (e.g. a new page → screens, a new endpoint → apis, a new table → tables).

For each new item:

1. Read `.sdd/catalog.json` to confirm the type exists and get its `id_prefix`.
2. Determine the next sequential ID:
   - Open `docs/design/<type>/index.md` (create it from `catalog/templates/index.md.example` if absent).
   - Find the highest existing `<id_prefix>-NNN` number in the table. Next ID = that number + 1, zero-padded to 3 digits.
   - If no entries exist yet, start at 001.
3. Choose a slug: lowercase, hyphen-separated summary of the item name (e.g. `login`, `post-auth-login`, `users`).
4. Add a row to `docs/design/<type>/index.md`:
   ```
   | <id_prefix>-NNN | <title> | planned | [<feature>](../../specs/<feature>/spec.md) | [→](<id_prefix>-NNN-<slug>.md) |
   ```
5. Create `docs/design/<type>/<id_prefix>-NNN-<slug>.md` from `catalog/templates/definition.md.example`:
   - Set `id`, `title`, `status: planned`, `feature`, `updated: <today YYYY-MM-DD>`.
   - Write `## 仕様` content based on what the spec says about this item.

Never reuse an ID. Deprecated entries still occupy their number.

## During verify phase — confirm entries

After `sdd-reviewer` confirms the implementation:

1. In `docs/design/<type>/index.md`, change the matching row's status from `planned` to `confirmed`.
2. In `docs/design/<type>/<id>.md`:
   - Change frontmatter `status: planned` to `status: confirmed`.
   - Update `updated:` to today's date.
   - If the implementation diverged from the spec, revise `## 仕様` to match the actual state.

## Deprecating entries

When a spec removes or replaces a catalogued item:

1. In `index.md`, change the entry's status to `deprecated`.
2. In the definition file, change frontmatter `status` to `deprecated` and update `updated:`.
3. Do NOT delete the file — deprecated entries are kept for history.

## ID rules

- Format: `<id_prefix>-NNN` (e.g. SCR-001, API-012, TBL-003).
- Zero-pad to 3 digits minimum (001, 002, ..., 099, 100).
- IDs are sequential and permanent. Never reuse, even after deprecation.
- Scan `index.md` for the highest existing number to find the next available ID.
```

- [ ] **Step 2: Commit**

```bash
git add catalog/rules/catalog.md
git commit -m "feat(catalog): add agent rules for catalog maintenance"
```

---

### Task 4: Workflow Integration

**Files:**
- Modify: `rules/workflow.md`

- [ ] **Step 1: Read current `rules/workflow.md`**

Read the file to confirm the exact text of step 2 (Spec line).

Current step 2 line:
```
2. Spec — write `specs/<feature>/spec.md` from the agreed design. Acceptance criteria as checkable statements. Get human approval.
```

- [ ] **Step 2: Add catalog reference line after step 2 in `rules/workflow.md`**

Insert the following line immediately after the step 2 line (before step 3):

```
   - If `.sdd/catalog.json` exists: register new catalog entries as `planned` in `docs/design/` (see `catalog/rules/catalog.md`). Update to `confirmed` in the verify phase.
```

The result should look like:
```
2. Spec — write `specs/<feature>/spec.md` from the agreed design. Acceptance criteria as checkable statements. Get human approval.
   - If `.sdd/catalog.json` exists: register new catalog entries as `planned` in `docs/design/` (see `catalog/rules/catalog.md`). Update to `confirmed` in the verify phase.
3. Plan & Tasks — skill `writing-plans` ...
```

- [ ] **Step 3: Verify the edit looks correct**

Run: `grep -A2 "Acceptance criteria" rules/workflow.md`

Expected: shows the step 2 line followed by the new catalog line.

- [ ] **Step 4: Commit**

```bash
git add rules/workflow.md
git commit -m "feat(catalog): integrate catalog update step into workflow rules"
```

---

### Task 5: README Update

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the README section between orchestration and 導入手順**

Run: `grep -n "##" README.md`

Identify the line number of `## 導入手順（取り込み側プロジェクト）`.

- [ ] **Step 2: Insert catalog section before `## 導入手順（取り込み側プロジェクト）`**

Insert the following block immediately before the `## 導入手順（取り込み側プロジェクト）` heading:

```
## 機能単位カタログ（オプション）

画面一覧・API一覧・テーブル一覧などのシステム全体カタログを `catalog/` モジュールで管理できる。
Claude が spec 作成時（planned）と verify 完了時（confirmed）に自動更新する。

| コンポーネント | パス | 役割 |
|---|---|---|
| エージェントルール | `catalog/rules/catalog.md` | カタログ更新のタイミングと手順 |
| スキーマ | `catalog/schema/catalog.schema.json` | `.sdd/catalog.json` の定義 |
| テンプレート | `catalog/templates/` | 設定例・一覧・定義書の雛形 |

### 有効化手順（取り込み側）

```bash
# 1. カタログ種類を宣言
cp vendor/ai-sdd-guide/catalog/templates/catalog.json.example .sdd/catalog.json
# → プロジェクトに合わせて types を編集

# 2. CLAUDE.md に参照を追加
echo "@vendor/ai-sdd-guide/catalog/rules/catalog.md" >> CLAUDE.md
```

有効化後は `spec.md` 作成時に Claude が `docs/design/` 配下にカタログと定義書を自動生成する。

```

Note: The content contains nested code fences. Write the markdown correctly — the inner ```bash block should be inside the section.

- [ ] **Step 3: Verify placement**

Run: `grep -n "##" README.md`

Expected: "機能単位カタログ" section appears between "マルチエージェント・オーケストレーション" and "導入手順".

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add catalog module to README"
```

---

## Self-Review

**Spec coverage:**
- [x] `catalog/schema/catalog.schema.json` — Task 1
- [x] `catalog/templates/catalog.json.example` — Task 2
- [x] `catalog/templates/index.md.example` — Task 2
- [x] `catalog/templates/definition.md.example` — Task 2
- [x] `catalog/rules/catalog.md` — Task 3 (covers: planned/confirmed/deprecated lifecycle, ID assignment rules, skip-if-absent)
- [x] `rules/workflow.md` integration — Task 4
- [x] `README.md` update — Task 5

**No placeholders:** All tasks contain complete file content.

**Consistency check:**
- `id_prefix` pattern `^[A-Z][A-Z0-9-]*$` in schema is consistent with examples (SCR, API, TBL)
- Status values `planned` / `confirmed` / `deprecated` used consistently across schema description, templates, and rules
- Path `catalog/rules/catalog.md` referenced consistently in rules/workflow.md addition and README
- `docs/design/<type>/index.md` path consistent across spec, rules, and templates
