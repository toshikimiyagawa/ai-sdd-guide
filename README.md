# ai-sdd-guide

AIを使ったスペック駆動開発（SDD: Spec-Driven Development）のガイドライン。

このリポジトリは **正本** として各プロジェクトに `git submodule` で取り込み、
agent（Claude Code / Cursor / Copilot など）と人間が同じルールで開発するための土台を提供する。

> ⚠️ 中身（superpowers連携・subagent構成・各ルール本文）は議論中。現状は骨組みのみ。

## 構成

| パス | 対象 | 言語 | 役割 |
|------|------|------|------|
| `rules/` | agent | 英語 | 常時参照するルールの正本（命令形・簡潔） |
| `docs/` | 人間 | 日本語 | 方法論の解説・なぜ・全体像 |
| `templates/` | 両方 | - | spec / plan / tasks の雛形 |
| `integration/` | 取り込み側 | - | プロジェクトルートに置く薄い入口の見本 |

## 導入手順（取り込み側プロジェクト）

```bash
# 1. submodule として追加（配置パスは任意。例: vendor/ai-sdd-guide）
git submodule add <this-repo-url> vendor/ai-sdd-guide

# 2. ルートに薄い入口を配置（一度だけコピー）
cp vendor/ai-sdd-guide/integration/CLAUDE.md.example ./CLAUDE.md
cp vendor/ai-sdd-guide/integration/AGENTS.md.example ./AGENTS.md
```

`CLAUDE.md` / `AGENTS.md` はプロジェクトルートに無いとagentが自動で読まないため、
submodule（サブパス）には置かず、ルートの薄い入口から submodule 内の正本を参照させる。

## 更新の反映

```bash
git submodule update --remote vendor/ai-sdd-guide
```

正本を更新すれば、各プロジェクトはこのコマンドで一括追従できる。

## ワークフロー（Tier制 / 規模に応じて省略可）

| Tier | 対象 | 作るもの |
|------|------|---------|
| 0 | typo・docs・自明な修正 | 何も作らず実施 |
| 1 | 小さなbugfix・小機能 | 軽量spec（意図＋受入条件）のみ |
| 2 | 中〜大機能・設計変更 | spec → plan → tasks → 実装 → 検証 をフル |

詳細は `docs/01-workflow.md`、agent向けの強制ルールは `rules/workflow.md` を参照。
