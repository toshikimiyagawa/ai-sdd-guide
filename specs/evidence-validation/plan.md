# Plan: evidence-validation

## 目的

Issue #54 の scope に従い、verify evidence の JSON Schema と validator 検査を追加する。

## 実装手順

### T1. Evidence schema

- `orchestration/schema/evidence.schema.json` を追加する。
- `feature`, `commit_sha`, `entries` を required にする。
- `commit_sha` は `^[0-9a-fA-F]{40}$` に制約する。
- `entries` は 1 件以上にする。
- entry は `command_type`, `command`, `result`, `test_count` を required にする。
- `command_type` は `test`, `lint`, `build`, `other` の enum にする。
- `command_type: "test"` の場合、`test_count` は integer にする。
- `command_type` が `"test"` 以外の場合、`test_count` は `null` にする。
- top-level と nested entry の `additionalProperties` を `false` にする。

### T2. Schema tests

- `tests/test_evidence_schema.py` を追加する。
- valid evidence が schema validation に成功することを確認する。
- non-test entry で `test_count` が非 null の場合に失敗することを確認する。
- test entry で `test_count` が欠落している場合に失敗することを確認する。
- `commit_sha` が 40 桁 hex でない場合に失敗することを確認する。

### T3. Validator checks

- `integration/ci/sdd-validate.py` に `check_evidence(root, feature)` を追加する。
- `specs/<feature>/evidence.json` が存在しない場合は validation error にする。
- evidence を `evidence.schema.json` で schema validation する。
- `git -C <root> cat-file -e <commit_sha>^{commit}` で commit SHA の存在を確認する。
- Git check が失敗した場合は validation error にする。
- Tier 2 feature では `main()` から `check_evidence` を呼ぶ。

### T4. Validator tests

- valid evidence と既存 commit SHA で `check_evidence` が成功することを確認する。
- 40 桁 hex だが存在しない commit SHA で失敗することを確認する。
- `evidence.json` missing で fail closed することを確認する。
- validator entrypoint が missing/broken evidence で non-zero を返すことを確認する。

### T5. Verify evidence for this feature

- 実装完了 commit 後、`specs/evidence-validation/evidence.json` を作成する。
- `commit_sha` には実装完了 commit を記録する。
- full test suite と `sdd-validate.py` 実行結果を entries に記録する。
- active Tier 2 状態で `sdd-validate.py` が通ることを確認してから done-reset する。

## 実行する検証

```sh
PATH=/tmp/ai-sdd-guide-test-venv/bin:$PATH /tmp/ai-sdd-guide-test-venv/bin/pytest -q
PATH=/tmp/ai-sdd-guide-test-venv/bin:$PATH python3 integration/ci/sdd-validate.py
```
