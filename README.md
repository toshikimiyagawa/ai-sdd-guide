# ai-sdd-guide

AIを使ったスペック駆動開発 (SDD: Spec-Driven Development) のガイドライン。

各プロジェクトに `git submodule` で **正本** として取り込み、
AIエージェントと人間が同じルールで開発するための土台を提供する。

## 中心思想：設計と実装の分離
- **設計 (spec/plan/tasks/レビュー) = Claude のみ**（superpowers + subagent + hooks をフル活用）
- **実装 = どのエージェントでも可**（`specs/<feature>/` を契約として渡す）

## 構成
| パス | 対象 | 言語 | 役割 |
|---|---|---|---|
| `rules/` | agent | 英語 | 常時参照する強制ルール（命令形・簡潔） |
| `docs/` | 人間 | 日本語 | 方法論の解説 |
| `templates/` | 両方 | - | spec / plan / tasks 雛形 |
| `integration/` | 取り込み側 | - | ルート入口・hooks・CI・subagent定義の見本 |

## ワークフロー（Tier制）
| Tier | 対象 | 作るもの |
|---|---|---|
| 0 | typo・docのみ・自明な修正 | 何も作らず実施 |
| 1 | 小さなbugfix・小機能 | 軽量spec＋テスト |
| 2 | 中〜大機能・設計変更 | spec → plan → tasks → 実装 → 検証 |

## 守らせる仕組み（多層）
1. **Claude hooks** — 設計フェーズの逸脱をローカルで弾く（速い注意喚起・バイパス可）
2. **CI** — 全agent共通の権威ある門番（spec有無・テスト）。バイパス不可
3. **sdd-reviewer subagent** — 実装が凍結specに適合するか独立監査

## 導入手順（取り込み側プロジェクト）
```bash
# 1. submodule として追加（配置パスは任意。例: vendor/ai-sdd-guide）
git submodule add <this-repo-url> vendor/ai-sdd-guide

# 2. ルートに薄い入口を配置（一度だけコピー）
cp vendor/ai-sdd-guide/integration/CLAUDE.md.example ./CLAUDE.md
cp vendor/ai-sdd-guide/integration/AGENTS.md.example ./AGENTS.md

# 3. Claude hooks と subagent を取り込む（Claude 利用時）
mkdir -p .claude
cp vendor/ai-sdd-guide/integration/settings.json.example .claude/settings.json
cp -r vendor/ai-sdd-guide/integration/agents .claude/agents

# 4. CI を取り込む（テストコマンドはプロジェクトに合わせて差し替え）
mkdir -p .github/workflows
cp vendor/ai-sdd-guide/integration/ci/sdd-check.yml .github/workflows/
```

設計フェーズで superpowers を使う場合は、Claude Code のプラグインとして別途導入する（submoduleとは別）：
```
/plugin install superpowers@claude-plugins-official
```
スキルとSDDフェーズの対応は `docs/02-roles.md` を参照。

`.sdd/state.json`（Tier/フェーズの状態。hooks・CIが参照）は作業中に agent が作成・更新する。
雛形は `templates/sdd-state.example.json`、値の定義は `templates/sdd-state.schema.json`。

`CLAUDE.md` / `AGENTS.md` はプロジェクトルートに無いとagentが自動で読まないため、
submodule（サブパス）には置かず、ルートの薄い入口から submodule 内の正本を参照させる。

## 更新の反映
```bash
git submodule update --remote vendor/ai-sdd-guide
```

正本を更新すれば、各プロジェクトはこのコマンドで一括追従できる。破壊的変更はタグ (semver) で管理する。

詳細は `docs/`（人間向け）と `rules/`（agent向け正本）を参照。
