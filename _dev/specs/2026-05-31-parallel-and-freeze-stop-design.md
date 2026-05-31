# Design: Parallel Feature Work and Freeze Stop Rule

**Date:** 2026-05-31
**Status:** Approved
**Fixes:** Issue #22, Issue #23

## 概要

2つの運用上の問題をまとめて解決する：

1. **並列作業時の state.json 衝突（#22）** — feature-per-worktree パターンを公式手順として明文化する。スキーマ・フック・CI の変更は不要。
2. **Freeze 後の意図しない即実装（#23）** — `workflow.md` の Freeze ステップに明示的な STOP ルールを1行追加する。

## 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `rules/workflow.md` | Freeze ステップに STOP ルール追加 + 並列作業の worktree 手順を追記 |
| `docs/01-workflow.md` | 同内容の人間向け説明を追記 |

## Issue #22 — 並列作業の公式パターン

### 設計方針

`state.json` の構造変更・フック変更は行わない。git worktree を使えば各 worktree が独立した `.sdd/` ディレクトリを持つため、state と phase tracking が自動的に分離される。この事実を公式手順として明文化するだけで十分。

### `rules/workflow.md` への追記

Step 0（Tier 分類）の直後に以下のブロックを追加する：

```markdown
## Parallel features

To work on multiple features simultaneously, use a separate git worktree per feature.
Each worktree has its own `.sdd/` directory — state and phase tracking are automatically
isolated. Use the `superpowers:using-git-worktrees` skill to create the worktree.

Never share a single worktree across two features in progress at the same time.
```

### `docs/01-workflow.md` への追記

人間向けに同内容を「並列作業」セクションとして追記する：

> 複数の feature を同時に進める場合は、feature ごとに git worktree を使う。
> 各 worktree が独立した `.sdd/` ディレクトリを持つため、state.json の衝突が起きない。
> `superpowers:using-git-worktrees` スキルで worktree を作成する。

## Issue #23 — Freeze 後の停止ルール

### 設計方針

`workflow.md` の Freeze ステップ（Step 4）に STOP ルールを明示する。フレーズは「STOP」で始まり、何を待つべきかを明記する。スキーマへの `frozen` フェーズ追加は行わない（テキストルールで十分）。

### `rules/workflow.md` の変更

**変更前（Freeze ステップ）:**
```
4. Freeze — set `.sdd/state.json` `phase=implement`. This is the handoff gate to other agents.
```

**変更後:**
```
4. Freeze — set `.sdd/state.json` `phase=implement`. This is the handoff gate to other agents.
   STOP. Do not begin implementation in the same session as freeze.
   Wait for an explicit instruction to implement before proceeding.
```

### `docs/01-workflow.md` への追記

Freeze ステップの説明に対応する注記を追加する：

> Freeze（phase=implement への遷移）を行ったら、**同一セッションで実装を開始してはいけない**。
> 人間から明示的な「実装して」指示を受けてから実装フェーズに入ること。

## スコープ外

- `sdd-state.schema.json` への `frozen` フェーズ追加（テキストルールで十分なため）
- フック・CI ロジックの変更
- worktree の自動作成スクリプト追加
