# Issue #48: 実装タスク

## タスク一覧

- [x] T1: `integration/agents/sdd-reviewer.md` に Issue へのアクセス方法を追加。対応 AC: SAC-2
  - Issue URL と Body の受け取り手順を定義
- [x] T2: `integration/agents/sdd-reviewer.md` に 8 項目の Mandatory Issue Traceability Check を追加。対応 AC: SAC-1
  1. AC Traceability: 元 Issue の全 AC が traceability table に追跡されているか
  2. Scope Exclusions: scope 外要件に follow-up issue URL があるか
  3. State Consistency: `state.json` の `feature` / `tier` / `phase` が対象作業と一致するか
  4. Tasks.json Validity: 対象 feature が `tasks.json` に存在し schema-valid か
  5. Tasks.md Completion: `tasks.md` の完了状態と完了報告が一致するか
  6. Test Coverage: 各 AC が実行可能な test に対応するか（目視確認のみ不可）
  7. Fail-Open/Negative Tests: fail-open 経路と negative test 不足がないか
  8. Audit Trail: 実行した command・件数・commit SHA が証跡に含まれるか
- [x] T3: `integration/agents/sdd-reviewer.md` に Bootstrap Exemption Handling を追加。対応 AC: SAC-5
  - exemption-range findings と non-exempt findings を分離して報告
- [x] T4: `integration/agents/sdd-reviewer.md` に Evidence Test Count の検証を追加。対応 AC: SAC-6
  - `test_count` は実行した test runner の test 件数として扱う
- [x] T5: `orchestration/rules/orchestration.md` に Issue Diff Summary の指示を追加。対応 AC: SAC-3
  - Human approval 時に Issue との差分サマリを必須化
- [x] T6: `orchestration/rules/orchestration.md` に Independent Reviewer Requirement を追加。対応 AC: SAC-4
- [x] T7: `orchestration/templates/handoff.md.example` から "Before Freeze" セクションを削除
- [x] T8: `.DS_Store` を削除し `.gitignore` に追加
- [x] T9: `specs/issue-48/{spec,plan,tasks,traceability}` を作成
- [x] T10: `.sdd/tasks.json` に `issue-48` エントリを追加
- [x] T11: テストがパスすることを確認

## 完了条件

- すべての上記タスクが完了
- テストがすべてパス
- PR #56 に反映
