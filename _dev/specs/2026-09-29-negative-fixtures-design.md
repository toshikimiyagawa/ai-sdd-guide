# Design: Negative Fixtures for SDD Validator (#47)

Date: 2026-09-29
Issue: #47 (parent: #43)
Dependencies resolved: #52 (core validator), #53 (snapshot validator), #54 (evidence validator)

## 目的

`sdd-validate.py` が各失敗パターンを確実に検出することを、fixture ベースの RED/GREEN テストで証明する。
consumer repo (agents-devcontainer) の PR #54 で発生した不整合が PASS してしまった再発防止が動機。

## Validator チェック一覧（実装済み）

| # | 関数 | 条件 |
|---|------|------|
| 1 | `check_schema_state` | state.json スキーマ検証（常時） |
| 2 | `check_schema_tasks` | tasks.json スキーマ + active feature エントリ存在確認 |
| 3 | `check_schema_traceability` | traceability.json スキーマ（Tier 2） |
| 4 | `check_state_tasks_consistency` | state.json feature/phase と tasks.json エントリの一致 |
| 5 | `check_tasks_md_consistency` | tasks.md の全 checkbox 完了（phase=verify 時） |
| 6 | `check_traceability_internal` | 重複 spec_ac / task 未存在 / spec_ac 未定義 / test ファイル未存在 |
| 7 | `check_scope_out` | out-of-scope/deferred に reason + HTTP(S) followup_issue |
| 8 | `check_issue_snapshot` | snapshot スキーマ + body_hash + traceability AC 整合性 |
| 9 | `check_evidence` | evidence スキーマ + commit_sha 存在確認 |

## Fixture 構成

### ディレクトリ規則

```
tests/fixtures/
  fixture-<name>/        # negative（無効）— validator が ERROR を返すべき
  fixture-<name>-valid/  # valid（修正済み）— validator が PASS すべき
```

各ディレクトリは `--root` として validator に直接渡せる完全なファイルセット。
mutation recipe だけにしない（ファイルを省略しない）。

### Core fixtures（Check 2, 4, 5, 6, 7 対応）

| Fixture | 対応チェック | 再現するパターン |
|---------|-------------|-----------------|
| `fixture-incomplete-tasks` | #5 | phase=verify で tasks.md に未完了 checkbox が残る |
| `fixture-wrong-state` | #4 | state.json の feature が tasks.json に存在しない |
| `fixture-missing-tasks-entry` | #2 | tasks.json に active feature のエントリがない |
| `fixture-no-test-mapping` | #6 | traceability の test フィールドが存在しないテストファイルを指す |
| `fixture-scope-out-no-followup` | #7 | out-of-scope エントリに followup_issue URL がない |
| `fixture-phase-mismatch` | #4 | state.json phase と tasks.json entry phase が不一致 |
| `fixture-orphan-spec-ac` | #6 | traceability の spec_ac が spec.md に未定義 |
| `fixture-duplicate-spec-ac` | #6 | traceability に同一 spec_ac ID が重複 |

### Snapshot fixtures（Check 8 対応）

| Fixture | 再現するパターン |
|---------|-----------------|
| `fixture-weakened-ac` | snapshot の AC が traceability に未追跡（untracked_in_traceability） |
| `fixture-stale-snapshot-hash` | raw_body を改変したが body_hash が古いまま |
| `fixture-untracked-issue-ac` | traceability の issue_ac が snapshot に存在しない |

### Evidence fixtures（Check 9 対応）

| Fixture | 再現するパターン |
|---------|-----------------|
| `fixture-invalid-evidence-commit` | evidence.json の commit_sha が git リポジトリに存在しない |
| `fixture-non-test-count` | lint/build コマンドに test_count を付けて test 扱い（スキーマ違反） |
| `fixture-missing-test-count` | test コマンドに test_count がない（スキーマ違反） |

## テストファイル設計

### `tests/test_negative_fixtures.py`（新規）

既存の `test_sdd_validate.py` は変更しない。

```python
@pytest.mark.parametrize("fixture_name,expected_fragment", [
    ("fixture-incomplete-tasks", "unchecked item"),
    ("fixture-wrong-state",      "no entry for feature"),
    ("fixture-missing-tasks-entry", "no entry for feature"),
    ...
])
def test_negative_fixture_fails(fixture_name, expected_fragment):
    # subprocess で sdd-validate.py --root <fixture> を実行
    # exit code 1 かつ stderr に expected_fragment が含まれることを確認

@pytest.mark.parametrize("fixture_name", [
    "fixture-incomplete-tasks-valid",
    ...
])
def test_valid_fixture_passes(fixture_name):
    # exit code 0 を確認
```

### evidence commit SHA の扱い

- `fixture-invalid-evidence-commit`: `deadbeef` × 40 の偽 SHA → 自然に失敗
- `fixture-invalid-evidence-commit-valid`: テスト実行時に `git rev-parse HEAD` でリアル SHA を取得して evidence.json に inject（`tmp_path` fixture でコピー）。既存 `valid-active/` の先例と同じアプローチ。

## README

各 negative fixture ディレクトリに `README.md` を置き、以下を記載:

```
## 再現パターン
## 対応チェック番号と関数名
## 実行コマンド（RED確認）
## 修正版（-valid/）の GREEN コマンド
```

## CI

既存の `.github/workflows/tests.yml` が `pytest tests/` を実行しているため追加設定不要。

## 受入条件（Issue #47 より）

- [ ] PR #54 で発生した 6 パターン以上の negative fixture が存在する
- [ ] #52 core validator が検出すべき fixture が validator 直接実行で失敗する
- [ ] #53 snapshot validator が検出すべき fixture が validator 直接実行で失敗する
- [ ] #54 evidence validator が検出すべき fixture が validator 直接実行で失敗する
- [ ] 各 fixture の valid 版に対して validator が PASS する（GREEN）
- [ ] tests が CI で自動実行される
- [ ] fixture の README に「どのパターンを再現しているか」が記載されている
