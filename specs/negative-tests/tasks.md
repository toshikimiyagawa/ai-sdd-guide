# Tasks: negative-tests

- [ ] T1: `tests/test_negative_fixtures.py` のスケルトンを作成し `fixture-incomplete-tasks` ペア（negative + valid）で RED/GREEN を確認する。AC: SAC-1, SAC-2, SAC-3, SAC-4
- [ ] T2: state/tasks 整合性 fixture 3 本（`fixture-wrong-state`, `fixture-missing-tasks-entry`, `fixture-phase-mismatch`）とそれぞれの valid 版を追加しテストを拡張する。AC: SAC-1, SAC-2, SAC-3
- [ ] T3: traceability 内部整合性 fixture 3 本（`fixture-no-test-mapping`, `fixture-orphan-spec-ac`, `fixture-duplicate-spec-ac`）とそれぞれの valid 版を追加しテストを拡張する。AC: SAC-1, SAC-2, SAC-3
- [ ] T4: scope-out fixture 1 本（`fixture-scope-out-no-followup`）と valid 版を追加しテストを拡張する。AC: SAC-1, SAC-2, SAC-3
- [ ] T5: snapshot fixture 3 本（`fixture-weakened-ac`, `fixture-stale-snapshot-hash`, `fixture-untracked-issue-ac`）とそれぞれの valid 版を追加しテストを拡張する。AC: SAC-1, SAC-2, SAC-3
- [ ] T6: evidence fixture 3 本（`fixture-invalid-evidence-commit`, `fixture-non-test-count`, `fixture-missing-test-count`）とそれぞれの valid 版を追加しテストを拡張する。AC: SAC-1, SAC-2, SAC-3, SAC-4
- [ ] T7: 全テストスイートを実行してリグレッションがないことを確認し PR を作成する。AC: SAC-4, SAC-5
