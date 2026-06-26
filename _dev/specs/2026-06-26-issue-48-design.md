# Issue #48 — Design Document

**Date:** 2026-06-26  
**Parent Issue:** #43  
**Status:** Implemented (PR #56)

## 目的

`sdd-reviewer` subagent と Claude agent（design/freeze フェーズ）が、frozen spec と元 Issue の差分を独立して検査するよう prompt と rules を更新する。実装者と同じコンテキストによる自己確認だけを最終 review としない。

## スコープ

### 1. `sdd-reviewer` prompt 更新

既存の spec 適合チェックに加えて、以下の 8 項目を確認項目として追加：

1. **AC Traceability**: 元 Issue の全 AC が traceability table に追跡されているか
2. **Scope Exclusions**: scope 外要件に follow-up issue URL があるか
3. **State Consistency**: `state.json` の `feature` / `tier` / `phase` が対象作業と一致するか
4. **Tasks.json Validity**: 対象 feature が `tasks.json` に存在し schema-valid か
5. **Tasks.md Completion**: `tasks.md` の完了状態と完了報告が一致するか
6. **Test Coverage**: 各 AC が実行可能な test に対応するか（目視確認のみ不可）
7. **Fail-Open/Negative Tests**: fail-open 経路と negative test 不足がないか
8. **Audit Trail**: 実行した command・件数・commit SHA が証跡に含まれるか

**Bootstrap Exemption Handling**:
- Bootstrap exemption がある場合、reviewer は対象 artifact と期限を明示し、exemption 外の finding まで skip しない。
- exemption-range findings と non-exempt findings を分離して報告する。

**Evidence Test Count**:
- `test_count` は実行した test runner の test 件数として扱う。compile 対象 file 数や shell script 数を test 件数として報告しない。

### 2. Claude agent（design/freeze）の prompt/rules 更新

- Human approval 時に `design 本文` + `元 Issue との差分サマリ` を必ず提示する。
- Handoff 生成前に traceability table の完全性を自己チェックする手順を追加。
- 独立 reviewer（`sdd-reviewer`）による反証的 review を必須ステップとして明記。

### 3. 独立 reviewer による review の必須化

- 設計/実装に関わった agent とは異なるコンテキストから adversarial review を行う。
- `sdd-reviewer` subagent を verify phase で必須呼び出し。

## 実装詳細

### 変更ファイル

1. **`integration/agents/sdd-reviewer.md` / `integration/prompts/sdd-reviewer-prompt.md`**
   - Issue へのアクセス方法（Issue URL, Body）を定義
   - 8 項目の Mandatory Issue Traceability Check を追加
   - Bootstrap Exemption Handling を追加
   - Evidence Test Count の検証を追加

2. **`orchestration/templates/handoff.md.example`**
   - "Before Freeze" セクションを削除（rules 側へ移動済み）

3. **`orchestration/rules/orchestration.md`**
   - "Rules for design agents" に Issue Diff Summary の指示を追加
   - Human approval 時に Issue との差分サマリを必須化

4. **`.gitignore`**
   - `.DS_Store` を追加
   - `.worktrees/` と `**/__pycache__/` の両方を保持

### 受入条件の検証

- [x] `sdd-reviewer` の prompt/instructions に 8 項目の確認が追加されている
- [x] Claude agent の freeze フェーズ instructions に「元 Issue との差分サマリ提示」が追加されている
- [x] `sdd-reviewer` が元 Issue へのアクセス方法（issue URL, body）を受け取る手順が定義されている
- [x] 独立 reviewer による review が workflow の必須ステップとして rules に明記されている（#45 と整合）
- [x] Reviewer が bootstrap exemption の範囲と exemption 外 finding を分離して報告する
- [x] Evidence の test 件数が実 test command の件数であることを確認する

## 依存関係

- 依存: #44（traceability 形式定義）、#45（rules 更新）
- ブロックする: #49（migration guide）

## 担当境界と証跡解釈

- Snapshot/evidence schema・生成・機械検査は#46 が所有し、この Issue は reviewer の意味的検査だけを所有する。
- `test_count` は実行した test runner の test 件数として扱う。compile 対象 file 数や shell script 数を test 件数として報告しない。

## テスト

- `tests/test_rules_freeze_verify.py` に reviewer prompt / orchestration rule / issue-48 traceability の回帰テストを追加
- 全テストがパス

## 次のステップ

- PR #56 のレビュー待ち
- マージ後、#49（migration guide）へ進む
