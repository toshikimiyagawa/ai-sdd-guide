# Issue #54: Verification evidence JSON Schema + validator検証を実装する

## 概要

verify フェーズの証跡を `specs/<feature>/evidence.json` として機械検査可能にし、
validator が evidence schema と commit SHA の存在を検査できるようにする。

これにより、目視確認・compile / syntax check・lint / build を test 件数として扱う
弱い証跡を schema / validator で拒否する。

## 受入条件

- [ ] SAC-1: `orchestration/schema/evidence.schema.json` が存在し、全フィールドを定義している（元 Issue: 54-AC1）
- [ ] SAC-2: `command_type: "test"` 以外のエントリで `test_count` が非 null の場合 schema validation が失敗する（元 Issue: 54-AC2）
- [ ] SAC-3: `command_type: "test"` のエントリで `test_count` が欠落している場合 schema validation が失敗する（元 Issue: 54-AC3）
- [ ] SAC-4: `commit_sha` が 40 桁 hex でない場合 schema validation が失敗する（元 Issue: 54-AC4）
- [ ] SAC-5: validator が `commit_sha` の git 存在チェックを実行できる（元 Issue: 54-AC5）
- [ ] SAC-6: validator が evidence 検査不能時に fail closed する（元 Issue: 54-AC6）

## スコープ

### 1. Verification evidence JSON Schema

**場所:** `orchestration/schema/evidence.schema.json`

**フィールド:**

- `feature`: string
- `commit_sha`: string, 40 桁 hex
- `entries`: array of command evidence entries
  - `command_type`: `test` | `lint` | `build` | `other`
  - `command`: string
  - `result`: string
  - `test_count`: integer | null

schema は top-level と `entries` item の追加 property を拒否する。

`test_count` は以下の条件を満たす。

- `command_type: "test"` の場合は必須の integer
- `command_type` が `"test"` 以外の場合は必須の `null`

### 2. Validator 拡張

**場所:** `integration/ci/sdd-validate.py`

Tier 2 feature の validator は `evidence.json` を必須 artifact として扱い、
以下を検査する。

- evidence が存在し schema-valid である
- `commit_sha` が Git repository 内に存在する
- evidence が存在しない、壊れている、または git で検査不能な場合に non-zero で終了する

### 3. Evidence artifact

**場所:** `specs/<feature>/evidence.json`

この artifact は verify フェーズ完了時に作成する。実装完了時の commit SHA と、
実行した検証コマンドの要約を保存する。

## 明示的にスコープ外

- state/tasks schema と core validator entrypoint（#52）
- Issue snapshot / Issue本文AC差分検査（#53）
- negative fixture 一式（#47）
- migration guide（#49）

## テスト

- `tests/test_evidence_schema.py::test_valid_evidence_passes_schema`
- `tests/test_evidence_schema.py::test_non_test_entry_with_test_count_fails_schema`
- `tests/test_evidence_schema.py::test_test_entry_missing_test_count_fails_schema`
- `tests/test_evidence_schema.py::test_invalid_commit_sha_fails_schema`
- `tests/test_sdd_validate.py::test_check_evidence_valid_existing_commit`
- `tests/test_sdd_validate.py::test_check_evidence_nonexistent_commit_fails`
- `tests/test_sdd_validate.py::test_check_evidence_missing_fails_closed`
