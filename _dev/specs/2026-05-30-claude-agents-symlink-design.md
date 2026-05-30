# Design: CLAUDE.md → AGENTS.md Symlink

**Date:** 2026-05-30
**Status:** Approved

## 概要

`CLAUDE.md` を `AGENTS.md` のシンボリックリンクとして管理する。`AGENTS.md` を正本とし、全 agent が同じ内容を読む。本リポジトリ (`ai-sdd-guide`) と取り込み元プロジェクトの両方を対象とする。

## 変更方針

- `AGENTS.md` = 実ファイル（正本）
- `CLAUDE.md` = `AGENTS.md` への symlink（`ln -s AGENTS.md CLAUDE.md`）
- `@` include 構文（Claude Code 専用）は廃止し、プレーンテキストでルールファイルへのパスを明示する
- "CLAUDE.md は symlink として維持すること" をファイル内容・update.sh・README の3箇所で明示する

## 変更ファイル一覧

### このリポジトリ (`ai-sdd-guide`)

| ファイル | 変更内容 |
|---|---|
| `AGENTS.md` | 新規作成。ルールファイルへのパス + superpowers 保存先 + symlink 維持の指示 |
| `CLAUDE.md` | 実ファイル → `AGENTS.md` への symlink に置き換え |

### 取り込み元プロジェクト向けテンプレート

| ファイル | 変更内容 |
|---|---|
| `integration/AGENTS.md.example` | 統一内容に書き直し（`@` include 廃止、設計+実装フェーズ両対応、symlink 指示追記） |
| `integration/CLAUDE.md.example` | 実ファイル → `AGENTS.md.example` への symlink に置き換え |
| `integration/update.sh` | `protected` から `CLAUDE.md` を除去。symlink 生成ロジックを追加（既存 symlink はスキップ、実ファイルなら警告） |
| `README.md` | セットアップ手順の step 2 を `cp CLAUDE.md.example` → `ln -s AGENTS.md CLAUDE.md` に変更 |

## 詳細仕様

### `AGENTS.md`（このリポジトリ）の内容

```markdown
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
```

### `integration/AGENTS.md.example` の内容

```markdown
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
```

### `integration/update.sh` の変更

`protected` 配列から `CLAUDE.md:...` を除去。末尾に symlink 生成ブロックを追加：

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

### `README.md` セットアップ手順

```bash
# 2. ルートに薄い入口を配置（一度だけコピー）
cp vendor/ai-sdd-guide/integration/AGENTS.md.example ./AGENTS.md
ln -s AGENTS.md CLAUDE.md        # CLAUDE.md は AGENTS.md のシンボリックリンクとして管理
```

## スコープ外

- `GEMINI.md` の追加・管理（Gemini CLI は GEMINI.md を読むが、今回の対象外）
- Windows での symlink 対応（git `core.symlinks=false` 環境）
- hooks や CI による symlink の自動チェック
