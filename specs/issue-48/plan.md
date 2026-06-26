# Issue #48: 実装計画

## 概要

Issue #48 の実装アプローチと影響範囲。

## アプローチ

### 1. `sdd-reviewer` prompt 更新

**ファイル:** `integration/agents/sdd-reviewer.md`, `integration/prompts/sdd-reviewer-prompt.md`

**変更:**
- Issue へのアクセス方法を定義（Issue URL, Body の受け取り手順）
- 8 項目の Mandatory Issue Traceability Check を追加
- Bootstrap Exemption Handling を追加
- Evidence Test Count の検証を追加

### 2. `orchestration/rules/orchestration.md` 更新

**変更:**
- "Rules for design agents" に Issue Diff Summary の指示を追加
- Human approval 時に Issue との差分サマリを必須化

### 3. `orchestration/templates/handoff.md.example` 整理

**変更:**
- "Before Freeze" セクションを削除（rules 側へ統合済み）

### 4. 不要ファイルの削除

**変更:**
- `.DS_Store` を削除
- `.gitignore` に `.DS_Store` を追加

### 5. SDD artifacts 作成

**変更:**
- `specs/issue-48/{spec,plan,tasks,traceability}` を作成
- `.sdd/tasks.json` に `issue-48` エントリを追加

## 影響範囲

- **ドキュメント更新:** `integration/agents/sdd-reviewer.md`, `orchestration/rules/orchestration.md`, `orchestration/templates/handoff.md.example`
- **SDD artifacts 作成:** `specs/issue-48/` 以下
- **設定更新:** `.gitignore`, `.sdd/tasks.json`
- **ファイル削除:** `.DS_Store`

## テスト戦略

- `tests/test_rules_freeze_verify.py` に reviewer prompt / orchestration rule / issue-48 traceability の回帰テストを追加
- 全テストがパスすることを確認

## リスク

- **低:** prompt/rules/artifact 更新のみで、実行時コードには影響なし
