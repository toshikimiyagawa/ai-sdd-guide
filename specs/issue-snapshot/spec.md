# Issue #53: Issue snapshot CLI + snapshot JSON Schema

## 概要

GitHub Issue 本文を `issue-snapshot.json` として保存し、Issue 由来の AC と
frozen spec / traceability の差分を validator で検出できるようにする。

## 受入条件

- [ ] SAC-1: `orchestration/schema/issue-snapshot.schema.json` が存在し、全フィールドを定義している（元 Issue: 53-AC1）
- [ ] SAC-2: snapshot CLI が Issue 番号を引数に `issue-snapshot.json` を生成できる（元 Issue: 53-AC2）
- [ ] SAC-3: `body_hash` が `raw_body` の SHA-256 hex digest と一致することを validator が検出できる（元 Issue: 53-AC3）
- [ ] SAC-4: `stable_acs` の `id` が `<issue番号>-AC<連番>` パターンに一致する（元 Issue: 53-AC4）
- [ ] SAC-5: validator が `stable_acs` と `traceability.json entries` の不一致を検出できる（元 Issue: 53-AC5）
- [ ] SAC-6: validator が Issue AC 未追跡を exit non-zero で検出できる（元 Issue: 53-AC6）
- [ ] SAC-7: validator が snapshot 検査不能時に fail closed する（元 Issue: 53-AC7）

## スコープ

### 1. Issue snapshot JSON Schema

**場所:** `orchestration/schema/issue-snapshot.schema.json`

**フィールド:**

- `issue`: integer
- `url`: string, `uri`
- `fetched_at`: string, `date-time`
- `raw_body`: string
- `body_hash`: lowercase SHA-256 hex digest
- `stable_acs`: array of ordered Issue AC entries
  - `id`: `<issue番号>-AC<連番>` 形式
  - `text`: AC テキスト

schema は top-level と `stable_acs` entry の追加 property を拒否する。

### 2. Issue snapshot CLI

**場所:** `integration/ci/sdd-issue-snapshot.sh`

Issue 番号と feature 名を受け取り、`gh issue view <N> --json body,title,url`
で取得した本文から `specs/<feature>/issue-snapshot.json` を生成する。

AC 抽出は `## 受入条件` section 配下の markdown task-list item を対象とし、
出現順に `<issue>-AC<N>` を割り当てる。Issue 本文は編集しない。

テスト容易性のため、実装は local body input を受け取れる Python helper に委譲してよい。

### 3. Validator 拡張

**場所:** `integration/ci/sdd-validate.py`

Tier 2 feature の validator は `issue-snapshot.json` を必須 artifact として扱い、
以下を検査する。

- snapshot が存在し schema-valid である
- `body_hash` が `raw_body` の SHA-256 と一致する
- `stable_acs[].id` が `issue` と配列順序から決まる ID と一致する
- snapshot 内の Issue AC がすべて `traceability.json entries[].issue_ac` に存在する
- `traceability.json entries[].issue_ac` が snapshot にない Issue AC を参照していない

snapshot が存在しない、壊れている、hash が一致しない、または対応関係を検査できない場合、
validator は non-zero で終了する。

## 明示的にスコープ外

- state/tasks schema と core validator entrypoint（#52）
- verification evidence schema / evidence.json / commit SHA 検査（#54）
- negative fixture 一式（#47）
- migration guide（#49）

## テスト

- `tests/test_issue_snapshot_schema.py::test_valid_issue_snapshot_passes_schema`
- `tests/test_issue_snapshot_schema.py::test_invalid_stable_ac_id_fails_schema`
- `tests/test_issue_snapshot_cli.py::test_cli_writes_snapshot_from_body_file`
- `tests/test_sdd_validate.py::test_check_issue_snapshot_hash_mismatch`
- `tests/test_sdd_validate.py::test_check_issue_snapshot_stable_ac_id_mismatch`
- `tests/test_sdd_validate.py::test_check_issue_snapshot_traceability_mismatch`
- `tests/test_sdd_validate.py::test_check_issue_snapshot_untracked_issue_ac`
- `tests/test_sdd_validate.py::test_check_issue_snapshot_missing_fails_closed`
