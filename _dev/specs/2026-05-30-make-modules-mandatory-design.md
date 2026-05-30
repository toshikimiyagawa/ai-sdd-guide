# Design: Make Orchestration and Catalog Modules Mandatory

**Date:** 2026-05-30
**Status:** Approved

## 概要

マルチエージェント・オーケストレーション (`orchestration/`) と機能単位カタログ (`catalog/`) を、すべての取り込み元プロジェクトで必須モジュールとする。README の「オプション」表記と「有効化手順」セクションを削除し、AGENTS.md.example に両モジュールのルールファイルを常時参照として追加する。カタログは `.sdd/catalog.json` が無い場合、エージェントが人間と会話してファイルを作成する初期化フローに変更する。

## 変更ファイル一覧

| ファイル | 変更内容 |
|---|---|
| `integration/AGENTS.md.example` | orchestration + catalog ルールファイルを "Read before any work" リストに追加 |
| `AGENTS.md` | 同上（このリポジトリ自身） |
| `catalog/rules/catalog.md` | "skip if absent" → 人間と相談して初期化するフローに変更 |
| `README.md` | "(オプション)" を削除、有効化手順セクション2つを削除、構成テーブルに orchestration/・catalog/ 行を追加 |
| `docs/00-overview.md` | 全体像テーブルに orchestration/・catalog/ 行を追加 |

## Section 1 — AGENTS.md.example / AGENTS.md の変更

### `integration/AGENTS.md.example`

"Read the canonical rules before any work:" リストに以下を追加：

```
- `vendor/ai-sdd-guide/orchestration/rules/orchestration.md`
- `vendor/ai-sdd-guide/catalog/rules/catalog.md`
```

既存の Verify phase セクションはそのまま維持する。

### `AGENTS.md`（このリポジトリ）

"Read before any work:" リストに以下を追加：

```
- `orchestration/rules/orchestration.md`
- `catalog/rules/catalog.md`
```

## Section 2 — カタログ初期化フロー（`catalog/rules/catalog.md`）

現在の "When to apply" 冒頭：
> Only apply these rules when `.sdd/catalog.json` exists. If the file is absent, skip all catalog steps entirely.

変更後：
> If `.sdd/catalog.json` is absent, initialize it before proceeding:
> 1. Ask the human: "Which catalog types should this project track? Examples: screens (SCR), apis (API), tables (TBL), jobs (JOB), events (EVT). Add any custom types you need."
> 2. Create `.sdd/catalog.json` with the chosen types using the schema in `catalog/schema/catalog.schema.json`.
> 3. Commit with message: `chore: initialize sdd catalog`
> 4. Proceed with the normal catalog flow.

その後の "When to apply" 条件（absent = skip）は削除し、「`.sdd/catalog.json` が存在する」前提で書き直す。

## Section 3 — README.md の変更

### 変更点 1：構成テーブルに行を追加

```markdown
| `orchestration/` | 両方 | - | マルチエージェント・オーケストレーション |
| `catalog/`       | 両方 | - | 機能単位カタログ |
```

### 変更点 2：セクション見出しから「（オプション）」を削除

- `## マルチエージェント・オーケストレーション（オプション）` → `## マルチエージェント・オーケストレーション`
- `## 機能単位カタログ（オプション）` → `## 機能単位カタログ`

### 変更点 3：有効化手順セクションを削除

以下の2つのサブセクションを丸ごと削除する：

**orchestration の有効化手順：**
```bash
# 1. AGENTS.md に1行追加
echo "@vendor/ai-sdd-guide/orchestration/rules/orchestration.md" >> AGENTS.md
# 2. AGENTS.md に追記（orchestration/integration/AGENTS-patch.md.example 参照）
# 3. CI に orchestration ジョブを追加（integration/ci/sdd-check.yml 参照）
```

**catalog の有効化手順：**
```bash
# 1. カタログ種類を宣言
cp vendor/ai-sdd-guide/catalog/templates/catalog.json.example .sdd/catalog.json
# → プロジェクトに合わせて types を編集
# 2. AGENTS.md に参照を追加
echo "@vendor/ai-sdd-guide/catalog/rules/catalog.md" >> AGENTS.md
```

有効化後の説明文（"有効化後は `spec.md` 作成時に..."）も削除する。

## スコープ外

- orchestration CI ジョブの必須化（現状の CI 設定は変えない）
- `catalog/rules/catalog.md` の初期化フロー以外の変更
- GEMINI.md・AGENTS-patch.md.example の変更
- Windows symlink 対応
