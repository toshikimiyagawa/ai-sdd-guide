# Issue #48: sdd-reviewer と Claude agent の prompt に元 Issue 差分検査を追加する

## 概要

`sdd-reviewer` subagent と Claude agent（design/freeze フェーズ）が、frozen spec と元 Issue の差分を独立して検査するよう prompt と rules を更新する。実装者と同じコンテキストによる自己確認だけを最終 review としない。

## 受入条件

- [x] `sdd-reviewer` の prompt/instructions に 8 項目の確認が追加されている
- [x] `sdd-reviewer` が元 Issue へのアクセス方法（Issue URL, body）を受け取る手順が定義されている
- [x] Claude agent の freeze フェーズ instructions に「元 Issue との差分サマリ提示」が追加されている
- [x] 独立 reviewer による review が workflow の必須ステップとして rules に明記されている（#45 と整合）
- [x] Reviewer が bootstrap exemption の範囲と exemption 外 finding を分離して報告する
- [x] Evidence の test 件数が実 test command の件数であることを確認する

## スコープ

### 1. `sdd-reviewer` prompt 更新

**場所:** `integration/agents/sdd-reviewer.md`

**変更内容:**
- Issue へのアクセス方法（Issue URL, Body）を定義
- 8 項目の Mandatory Issue Traceability Check を追加:
  1. AC Traceability: 元 Issue の全 AC が traceability table に追跡されているか
  2. Scope Exclusions: scope 外要件に follow-up issue URL があるか
  3. State Consistency: `state.json` の `feature` / `tier` / `phase` が対象作業と一致するか
  4. Tasks.json Validity: 対象 feature が `tasks.json` に存在し schema-valid か
  5. Tasks.md Completion: `tasks.md` の完了状態と完了報告が一致するか
  6. Test Coverage: 各 AC が実行可能な test に対応するか（目視確認のみ不可）
  7. Fail-Open/Negative Tests: fail-open 経路と negative test 不足がないか
  8. Audit Trail: 実行した command・件数・commit SHA が証跡に含まれるか
- Bootstrap Exemption Handling を追加
- Evidence Test Count の検証を追加

### 2. Claude agent（design/freeze）の prompt/rules 更新

**場所:** `orchestration/rules/orchestration.md`

**変更内容:**
- Human approval 時に `design 本文` + `元 Issue との差分サマリ` を必ず提示する
- Handoff 生成前に traceability table の完全性を自己チェックする手順を追加

### 3. 独立 reviewer による review の必須化

**場所:** `orchestration/rules/orchestration.md`

**変更内容:**
- 設計/実装に関わった agent とは異なるコンテキストから adversarial review を行う
- `sdd-reviewer` subagent を verify phase で必須呼び出し

## 依存関係

- 依存: #44（traceability 形式定義）、#45（rules 更新）
- ブロックする: #49（migration guide）

## 担当境界と証跡解釈

- Snapshot/evidence schema・生成・機械検査は#46 が所有し、この Issue は reviewer の意味的検査だけを所有する。
- `test_count` は実行した test runner の test 件数として扱う。compile 対象 file 数や shell script 数を test 件数として報告しない。

## テスト

- 既存の 21 テストはすべてパス
- 変更はドキュメント更新のみ（コード変更なし）
