# Tasks: traceability-format

## 実装タスク（順序付き）

- [x] T1: `orchestration/schema/traceability.schema.json` を作成する。対応 AC: SAC-1, SAC-2, SAC-3
- [x] T2: `tests/test_traceability_schema.py` を作成する。対応 AC: SAC-1, SAC-2, SAC-3
- [x] T3: `templates/traceability.json.example` を作成する。対応 AC: SAC-4
- [x] T4: `docs/traceability.md` を作成する。対応 AC: SAC-5
- [x] T5: `templates/spec.md` に traceability 参照行・SAC-N 形式を追加する。対応 AC: SAC-6

## テスト（受入条件との対応・必須）

- [x] SAC-1 → test: `tests/test_traceability_schema.py::test_valid_in_scope_passes`
- [x] SAC-2 → test: `tests/test_traceability_schema.py::test_in_scope_missing_spec_ac_fails`, `test_in_scope_missing_task_fails`, `test_in_scope_missing_test_fails`, `test_in_scope_invalid_task_format_fails`, `test_in_scope_invalid_test_format_fails`
- [x] SAC-3 → test: `tests/test_traceability_schema.py::test_out_of_scope_missing_reason_fails`, `test_out_of_scope_missing_followup_issue_fails`, `test_out_of_scope_nonnull_spec_ac_fails`, `test_out_of_scope_nonnull_task_fails`, `test_out_of_scope_nonnull_test_fails`, `test_empty_reason_fails`, `test_mailto_followup_issue_fails`, `test_ftp_followup_issue_fails`
- [x] SAC-4 → test: `tests/test_traceability_schema.py::test_valid_out_of_scope_passes`, `test_valid_deferred_passes`
- [x] SAC-5 → 手動確認: `docs/traceability.md` が命名規則・freeze checklist を含む
- [x] SAC-6 → 手動確認: `templates/spec.md` が traceability 参照行・SAC-N 形式を含む
- [x] SAC-7 → `orchestration/schema/traceability.schema.json` が存在し、`templates/traceability.json.example` が schema valid

## 完了の定義

- [x] 全 AC 対応テストが green（19/19 PASS）
- [ ] CI green
- [ ] sdd-reviewer 合格
