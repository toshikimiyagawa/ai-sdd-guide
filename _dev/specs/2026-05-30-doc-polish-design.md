# Design: Documentation Polish — Remove Claude-Only Language

**Date:** 2026-05-30
**Status:** Approved

## 概要

リポジトリ全体のドキュメントから「Claude のみ」という制約表現を除去し、「superpowers が使えるエージェントなら誰でも設計・検証フェーズを担当できる」という実態に合わせる。あわせて、エージェント向けファイルに混入している日本語行を英語化する。

## 変更方針

制約の軸を「エージェントの種類（Claude）」から「ケーパビリティ（superpowers インストール済み）」に統一する。

| 現行表現 | 変更後 |
|---|---|
| 設計 = Claude のみ | 設計 = superpowers 必須（どのエージェントでも可） |
| 検証（Claude） | 検証（superpowers 必須） |
| Claude Code 専用プラグイン | Claude/Codex/Gemini 対応プラグイン |
| 実装 = 任意のagent | そのまま（変更なし） |

**例外:** `rules/subagents.md` のサブエージェント dispatch 方法（Task tool / Agent tool）は Claude Code 固有のメカニズムなので「Claude Code」の記載は残す。ただしタイトルの「design/verify only」制限ニュアンスは削除する。

## 変更ファイル一覧

| ファイル | 変更内容 |
|---|---|
| `README.md` | 中心思想セクションの「Claude のみ」を「superpowers 必須、どのエージェントでも可」に変更 |
| `rules/core.md` | "Claude Code only" → "superpowers required, any agent" |
| `rules/workflow.md` | "Design phases (Claude only)" / "Verify phase (Claude)" 見出しを修正。日本語行を英語化 |
| `rules/subagents.md` | タイトルから "design/verify only" を削除 |
| `rules/conventions.md` | 日本語行を英語化（PR #10 の修正漏れ） |
| `docs/00-overview.md` | 「Claude のみ」表記を「superpowers 対応エージェントなら誰でも」に更新 |
| `docs/01-workflow.md` | 「設計（Claudeのみ）」「検証（Claude）」を更新 |
| `docs/02-roles.md` | Claude/他agent の役割記述を更新。superpowers を multi-agent 対応プラグインとして説明 |
| `catalog/rules/catalog.md` | タイトルから "Claude" を削除 |

## スコープ外

- ドキュメントの構造変更（ファイル追加・削除・移動）
- rules/ や docs/ の内容の大幅な加筆
- templates/ の変更
