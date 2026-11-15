# Tasks: 95-no-content-tests

> 他 agent が設計コンテキスト無しで実装できるよう、各タスクは具体的に書く。書く内容と共通の制約は plan.md、消すテストの一覧は spec.md の「消すテスト・残すテスト」を参照。
> テストは `uv run --no-project --with pytest --with jsonschema python -m pytest tests -q` で全体を流す。
> 動きを変えるタスク（T1）は、テストを先に書いて失敗を確かめてから直す（RED → GREEN）。文書だけのタスクにはテストを書かない。タスクごとにコミットする。

## 実装タスク（順序付き）
- [x] T1: `orchestration/schema/traceability.schema.json` の in-scope の `test` に `"diff"` を許す（plan.md）。テストを足す: `tests/test_traceability_schema.py::test_in_scope_test_accepts_diff`・`::test_in_scope_test_rejects_other_strings`、`tests/test_sdd_validate.py::test_traceability_diff_entry_passes`。`templates/traceability.json.example` の `50-AC2` の `test` を `"diff"` にする（既存の `tests/test_traceability_schema.py::test_example_is_schema_valid` が通ること）。対応AC: SAC-3, SAC-4
- [x] T2: rules を書き換える。`rules/core.md`・`rules/workflow.md`・`orchestration/rules/orchestration.md`（plan.md「変更の要点」）。対応AC: SAC-1
- [x] T3: reviewer を書き換える。`integration/agents/spec-reviewer.md`・`integration/prompts/spec-reviewer-prompt.md`・`integration/agents/sdd-reviewer.md`・`integration/prompts/sdd-reviewer-prompt.md`（plan.md）。対応AC: SAC-2
- [x] T4: テンプレート・docs・hook を合わせる。`templates/spec.md`・`templates/tasks.md`・`orchestration/templates/handoff.md.example`・`integration/AGENTS.md.example`・`integration/hooks/codex-skill-reminder.sh` の implement のメッセージ・`docs/01-workflow.md`・`docs/02-roles.md`・`docs/03-faq.md`・`docs/traceability.md`・`README.md`（plan.md）。hook のメッセージを変えたあと、既存の `tests/test_skill_reminder.py` が通ること。対応AC: SAC-4
- [x] T5: `docs/migration.md` の末尾に spec D2 の節を足す（SAC-6 の 5 項目）。対応AC: SAC-6
- [x] T6: spec.md の「消すテスト・残すテスト」のとおりに `tests/` を整理する。`test_spec_phase_reminder_mentions_spec_reviewer` を `tests/test_skill_reminder.py` に移してから `tests/test_ai_autonomy.py` を消す。最後に全体を流して通ることを確かめる。対応AC: SAC-5

## 確かめ方（受入条件との対応・必須）
- [x] SAC-1 → 差分: `rules/core.md`, `rules/workflow.md`, `orchestration/rules/orchestration.md`
- [x] SAC-2 → 差分: `integration/agents/spec-reviewer.md`, `integration/prompts/spec-reviewer-prompt.md`, `integration/agents/sdd-reviewer.md`, `integration/prompts/sdd-reviewer-prompt.md`
- [x] SAC-3 → test: `tests/test_traceability_schema.py::test_in_scope_test_accepts_diff`, `::test_in_scope_test_rejects_other_strings`, `tests/test_sdd_validate.py::test_traceability_diff_entry_passes`
- [x] SAC-4 → 差分: T4 のファイルと `templates/traceability.json.example`（`tests/test_traceability_schema.py::test_example_is_schema_valid` と `tests/test_skill_reminder.py` が通る）
- [x] SAC-5 → 差分: `tests/`（spec の一覧と突き合わせる）と、テストの全件実行が通ること
- [x] SAC-6 → 差分: `docs/migration.md`

## 完了の定義
- 全テスト green（`uv run --no-project --with pytest --with jsonschema python -m pytest tests -q`）
- `uv run -q --no-project --with jsonschema python integration/ci/sdd-validate.py --root . --pr --pr-labels sdd:tier-2` が PASS
- CI green / sdd-reviewer 合格（verify フェーズで確認）
（上のチェック欄はすべて `[x]` にしてから verify へ進む。この「完了の定義」はチェック欄にしない）
