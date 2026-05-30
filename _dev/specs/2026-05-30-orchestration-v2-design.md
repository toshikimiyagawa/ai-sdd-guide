# Design: Orchestration v2 — Pull-Based Multi-Agent Model

**Date:** 2026-05-30
**Status:** Approved

## 概要

現行のオーケストレーションモデルを「プッシュ型（Claudeが担当エージェントを決定）」から「プル型（人間が明示的に指示）」に変更する。あわせて設計フェーズの担当制約を「Claude のみ」から「superpowers インストール済みエージェントなら誰でも可」に緩和する。

## 変更の動機

- superpowers が Codex・Gemini にも対応しており、技術的に設計フェーズも実行できる
- `agent-assignment.json` によるルーティングより、人間が「このタスクをこのエージェントでやって」と直接指示する方がシンプルで柔軟
- フェーズ間を自動横断させず、完了のたびに停止・確認させることで人間のコントロールを強化する

## アーキテクチャ

### フェーズ割り当て（変更後）

| フェーズ | 担当 | 備考 |
|---|---|---|
| brainstorm / spec / plan / tasks | superpowers インストール済みエージェントなら誰でも | Claude・Codex・Gemini いずれも可 |
| implement | 人間が指示したエージェント | agent-assignment.json 廃止 |
| verify | superpowers インストール済みエージェントなら誰でも | sdd-reviewer プロンプトを使用 |

### フェーズ間の明示的停止

エージェントはフェーズを完了したら **必ず停止し、人間の次の指示を待つ**。フェーズを自動的にまたいではいけない。

停止時は kanban（`.sdd/tasks.json`）を表示して残タスクを人間に示す。

```
設計完了時:
  tasks.md を作成 → kanban 表示 → 停止（実装に進まない）

タスク実装完了時:
  実装コミット → kanban 表示 → 停止（verify に進まない）

verify 完了時:
  sdd-reviewer 結果を報告 → kanban 表示 → 停止
```

### 典型的なフロー

```
人間 → Gemini: "feat-login を設計して"
  Gemini: brainstorm → spec → plan → tasks → kanban 表示 → 停止

人間 → Codex: "T1（ログイン画面）を実装して"
  Codex: T1 実装 → kanban 表示 → 停止

人間 → Codex: "T2（API）を実装して"
  Codex: T2 実装 → kanban 表示 → 停止

人間 → Claude: "feat-login を verify して"
  Claude: sdd-reviewer 実行 → 結果報告 → kanban 表示 → 停止
```

### sdd-reviewer のマルチエージェント対応

- `integration/agents/sdd-reviewer.md` — Claude Code 向けサブエージェント定義としてそのまま残す
- `integration/prompts/sdd-reviewer-prompt.md` — YAML frontmatter なしの純粋な指示文を新規作成。Gemini（`@generalist`）・Codex（`spawn_agent`）はこのファイルの内容をサブエージェントに渡す

## 廃止するもの

| ファイル | 理由 |
|---|---|
| `orchestration/schema/agent-assignment.schema.json` | agent-assignment.json を廃止 |
| `orchestration/templates/agent-assignment.example.json` | 同上 |
| `orchestration/integration/hooks/sdd-orchestration-guard.sh` | assigned_agent によるブロック不要 |

## 変更するもの

| ファイル | 変更内容 |
|---|---|
| `orchestration/rules/orchestration.md` | フェーズ割り当て・停止ルール・設計エージェント向けルールを全面改訂 |
| `orchestration/integration/settings-patch.json` | guard hook の参照を削除 |
| `templates/sdd-state.schema.json` | `assigned_agent` フィールドを削除 |
| `templates/sdd-state.example.json` | `assigned_agent` フィールドを削除 |
| `integration/CLAUDE.md.example` | "Design phases: Claude only" の文言を削除 |
| `orchestration/integration/AGENTS-patch.md.example` | 設計フェーズも担当できる旨を追記 |
| `README.md` | orchestration セクションを新モデルに更新 |

## 新規作成するもの

| ファイル | 内容 |
|---|---|
| `integration/prompts/sdd-reviewer-prompt.md` | エージェント非依存の sdd-reviewer 指示文 |

## スコープ外

- 自動ディスパッチ機構（エージェントの空き検知など）
- kanban.sh の機能拡張
- CI の変更
- CI の `orchestration` ジョブ（`agent-assignment.json` 前提のチェックが含まれる場合は別途対応）
