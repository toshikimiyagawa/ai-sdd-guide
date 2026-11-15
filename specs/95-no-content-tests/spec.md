# Spec: 95-no-content-tests

- Tier: 2
- Feature slug: 95-no-content-tests
- Issue: #95
- Traceability: [traceability.json](traceability.json)

## 背景 / 意図

`rules/core.md` は「受入基準はすべてテストに対応させる」と定めている。そのため、文書・設定・データに特定の語句や値を書いたという受入基準まで、テストにしている（例: `tests/test_ai_autonomy.py` の `assert "never merge" in content`）。

この種類のテストは、書いた内容をもう一度確かめるだけで守るものが無い。変えたのなら理由があり、あとで正しく変えるたびに落ちて直す手間だけが増える。利用側（plansys-data #1722・#1723）でも同じ問題が出て、規約で禁じてテストを消した。guide の既定として取り込み、guide 自身の `tests/` からも該当するテストを消す。

方針（2026-11-15、人間と確認済み）: 規約を書き、guide 自身の既存の該当テストも消す。Tier 2。

## 用語と規則

### 書いた内容を確かめるだけのテスト（作らない）

次のどれかだけを確かめるテスト。

- 文書・rules・設定・データ・テンプレート・ワークフローの YAML に、特定の行・値・語句・見出し・キーがある（ない）こと。並び・件数を含む
- 固定のコミットから変わったのが特定の行だけであること
- スクリプトやコードのソースに、特定の式・語句が書いてあること

### 作るテスト

- コードの動き: スクリプト・hook・CLI・関数を入力を与えて動かし、出力・終了コード・作ったファイルを見る
- スキーマの検証: データやフィクスチャをスキーマにかけて、通る・落ちるを見る
- リポジトリ全体にかかる規約の機械検査: ある種類のファイルすべてにかかる検査（例: すべてのシェルスクリプトの移植性）
- 成果物どうしの整合: 一致しなければならない 2 つのもの（例: 参照しているパスが存在する）

### 差分で確かめる受入基準

データ・設定・文書・文言を書いた（変えた・消した）という受入基準は、テストにせず差分で確かめる。

- spec の受入基準ごとに、確かめ方（テスト / 差分）を書く
- Tier 2 の `tasks.md` のテストの節は「確かめ方」の節とし、差分で確かめる受入基準は `SAC-N → 差分: <ファイル>` と書く
- `traceability.json` では、差分で確かめる受入基準の `test` を文字列 `"diff"` にする
- `sdd-reviewer` は、差分で確かめる受入基準ごとに、満たしている差分の行（`<ファイル>:<行>`）を挙げて確かめる
- 動きを変える受入基準は、今までどおり通るテストに対応させる。「Tier 1 以上はテスト必須」は「Tier 1 以上で動きを変えるならテスト必須」にする

### 決めたこと（AI の判断）

- **D1 `traceability.json` の表し方**: 新しい欄を足さず、`test` に `"diff"` を許す。in-scope の `test` は `<ファイル>::<テスト名>` か `"diff"` のどちらか。`sdd-validate.py` のテストファイルの存在の検査は `::` を含むときだけ動くので、変えなくてよい。欄を足すとスキーマ・validator・既存の `traceability.json` のすべてに手が入るため
- **D2 版の名前**: `docs/migration.md` の節は `## v4.2: 書いた内容を確かめるだけのテストを作らない（#95）`
- **D3 過去の `specs/`**: 消すテストを指している過去の `specs/*/traceability.json`・`tasks.md` は書き換えない（凍結した成果物のため）。`sdd-validate.py` は今のブランチの feature だけを見るので、過去の参照が切れても CI は落ちない
- **D4 混ざったテスト**: 動きを確かめつつ書いた内容も確かめているテストは、関数を残し、書いた内容を確かめる assert だけを消す
- **D5 この feature 自身**: この spec の受入基準のうち rules・文書・テンプレートを変えるものは差分で確かめる（`traceability.json` の `test` は `"diff"`）。凍結の時点では今のスキーマが `"diff"` を受け付けないが、T1 でスキーマを変えたあとの `sdd-validate.py` で通ればよい

## 受入条件

- [ ] SAC-1: `rules/core.md`・`rules/workflow.md`・`orchestration/rules/orchestration.md` が、上の「書いた内容を確かめるだけのテスト（作らない）」「作るテスト」「差分で確かめる受入基準」を定めている。「受入基準はすべてテストに対応させる」「Tier 1 以上はテスト必須」「各 AC は実行できるテストに対応する」の記述は、動きを変える受入基準に限る形に置き換わっている。確かめ方: 差分（元 Issue: 95-AC1）
- [ ] SAC-2: `integration/agents/spec-reviewer.md`・`integration/prompts/spec-reviewer-prompt.md` の照合の項目が、受入基準ごとの確かめ方（テスト / 差分）と、書いた内容を確かめるだけのテストを計画していれば `CHANGES` にすることを含む。`integration/agents/sdd-reviewer.md`・`integration/prompts/sdd-reviewer-prompt.md` が、差分で確かめる受入基準は差分の行を挙げて確かめること、差分に書いた内容を確かめるだけのテストがあれば指摘することを含む。確かめ方: 差分（元 Issue: 95-AC2）
- [ ] SAC-3: `orchestration/schema/traceability.schema.json` で、in-scope の項目の `test` が `<ファイル>::<テスト名>` または `"diff"` を受け付け、それ以外の文字列（`::` を含まない、`"diff"` でない）を拒む。`"diff"` の項目を含む `traceability.json` で `sdd-validate.py` が通る。確かめ方: テスト（元 Issue: 95-AC3）
- [ ] SAC-4: `templates/spec.md`・`templates/tasks.md`・`templates/traceability.json.example`・`orchestration/templates/handoff.md.example`・`integration/AGENTS.md.example`・`integration/hooks/codex-skill-reminder.sh` の実装フェーズのメッセージ・`docs/01-workflow.md`・`docs/02-roles.md`・`docs/03-faq.md`・`README.md` に、すべての受入基準をテストにすることを求める記述がなく、確かめ方（テスト / 差分）の書き方と矛盾しない。確かめ方: 差分（元 Issue: 95-AC4）
- [ ] SAC-5: `tests/` から、下の「消すテスト」の関数（とその関数だけが使っていた補助関数・定数・import）が消え、関数が残らないファイルはファイルごと消えている。「残すテスト」は残り、`uv run --no-project --with pytest --with jsonschema python -m pytest tests -q` が通る。確かめ方: 差分（消したもの）と、テストの全件実行（元 Issue: 95-AC5）
- [ ] SAC-6: `docs/migration.md` に D2 の節があり、既存の consumer 向けに、規約が変わったこと、`traceability.json` の `test` に `"diff"` を書けること、`update.sh` で reviewer が配られること、`AGENTS.md` の「Every acceptance criterion must map to a passing test」を見直すこと、既存のテストを消すかは各リポジトリで決めることが書かれている。確かめ方: 差分（元 Issue: 95-AC6）

## 消すテスト・残すテスト

基準は上の「用語と規則」。関数名は `tests/<ファイル>::<関数>`。ここに無い関数はすべて残す。

### ファイルごと消す

- `tests/test_board_docs.py`（2 本すべて）
- `tests/test_docs_github_app.py`（4 本すべて）
- `tests/test_rules_freeze_verify.py`（18 本すべて。`test_issue_48_traceability_references_defined_artifacts` は過去の 1 feature だけを突き合わせるもので、同じ検査は `sdd-validate.py` の動きとして `tests/test_sdd_validate.py` が確かめている）
- `tests/test_ai_autonomy.py`（下の 11 本を消し、残る `test_spec_phase_reminder_mentions_spec_reviewer` は中身を変えずに `tests/test_skill_reminder.py` に移す。移したあと、このファイルは消す）
  - 消す: `test_orchestration_defines_human_touchpoints_and_autonomous_flow`, `test_escalation_conditions_listed_and_referenced`, `test_rules_have_no_old_stop_phrases`, `test_handoff_is_written_after_spec_review_and_freeze`, `test_rules_require_spec_review_before_freeze`, `test_weakening_acs_still_needs_human_approval`, `test_spec_reviewer_files_define_verdicts_and_limit`, `test_pr_body_template_has_ai_decision_log`, `test_surrounding_docs_have_no_old_stop_phrases`, `test_docs_describe_human_touchpoints`, `test_migration_has_v4_section`

### 関数を消す

- `tests/test_migration_guide.py`: `test_migration_guide_exists`, `test_migration_guide_has_all_sections`, `test_migration_guide_has_consumer_checklist`, `test_migration_guide_has_examples`, `test_migration_guide_no_retroactive_policy`, `test_migration_guide_no_partial_migration`, `test_migration_guide_projects_board_section`, `test_snapshot_examples_use_submodule_path_without_root`, `test_consumer_sections_use_submodule_paths`, `test_step4_and_checklist_follow_v3_state_derivation`, `test_step4_heading_has_no_v2_terms`, `test_step7_and_examples_have_no_state_files`。`test_step5_describes_actual_sdd_check_steps` は残し、`s not in step5` の形の 4 つの assert だけを消す（`sdd-check.yml` の全ステップ名が手順 5 に出てくるかの突き合わせは残す。D4）
- `tests/test_no_legacy_state.py`: `test_legacy_files_removed`
- `tests/test_readme_install.py`: `test_install_steps_include_optional_board_setup`, `test_install_steps_explain_no_board_and_tier_label`
- `tests/test_sdd_board_workflow.py`: `test_triggers`, `test_uses_project_token_secret`, `test_app_token_step`, `test_auth_mode_step`, `test_board_steps_use_app_or_pat_token`, `test_none_mode_warns_and_skips`, `test_label_step_uses_github_token`, `test_header_documents_auth_and_pat_scopes`, `test_pr_job_adds_tier_label`, `test_calls_board_subcommands`, `test_checkout_pr_head_with_submodules`, `test_forbidden_strings_absent`。モジュールの docstring の「(checked as text)」も合わせて直す
- `tests/test_sdd_check_submodule.py`: `test_sdd_job_checkout_fetches_submodules`, `test_no_state_reset_gate`, `test_no_orchestration_job`, `test_validate_step_passes_pr_context`, `test_migration_guide_uses_submodule_validator_path`, `test_readme_states_fixed_submodule_path`, `test_sdd_job_checkout_uses_guide_token_secret`, `test_ci_docs_explain_guide_token_secret`, `test_sdd_job_checkout_does_not_persist_credentials`, `test_pull_request_trigger_includes_label_events`, `test_board_workflows_document_token_scope_and_trust`, `test_update_sh_checks_python3`, `test_update_sh_preserves_submodule_fix`, `test_update_sh_preserves_guide_token_fallback`（最後の 2 本は書いた内容の確認を除くと `update.sh` の終了コードしか残らず、`tests/test_update_sh.py` と重なるため関数ごと消す）
- `tests/test_self_migration.py`: `test_legacy_state_files_absent`, `test_board_json_present`, `test_board_json_has_app_id`, `test_board_workflow_present`
- `tests/test_traceability_schema.py`: `test_schema_file_exists`, `test_docs_naming_convention`, `test_spec_template_uses_sac_format`

消した関数だけが使っていた補助関数・定数・import も消す（例: `test_migration_guide.py` の `SNAPSHOT_PREFIX`・`GUIDE_PATH`、`test_no_legacy_state.py` の `LEGACY_FILES`、`test_sdd_board_workflow.py` の `CLI`・`_on_block`・`_steps`・`_step`・`BOARD_STEPS`・`TOKEN_EXPR`、`test_sdd_check_submodule.py` の `MIGRATION`・`README`・`SUBMODULE_VALIDATOR`・`GUIDE_TOKEN`・`UPDATE_SH`・`_job_block`・`_assert_submodule_fix`・`_sdd_checkout_block`・使われなくなった `import`、`test_self_migration.py` の `import json`）。まだ使われているものは残す。

### 残すもの（境界の判断）

- `tests/test_no_legacy_state.py::test_no_legacy_instructions`・`tests/test_sdd_board_workflow.py::test_no_expression_interpolation_in_run_scripts`: ある種類のファイルすべてにかかる機械検査として残す
- `tests/test_self_migration.py::test_feature_freeze_valid`・`::test_validator_passes_for_this_feature`: このリポジトリで `sdd_state.py`・`sdd-validate.sh` を実際に動かすため残す
- `tests/test_sdd_board_workflow.py::test_repo_copy_matches_template`・`tests/test_readme_install.py::test_install_workflows_match_update_sh`・`tests/test_migration_guide.py` の `test_cli_examples_match_cli_options`・`test_submodule_paths_exist_in_guide`・`test_partial_migration_checklist_lists_existing_schemas`: 成果物どうしの整合として残す
- `tests/test_sdd_app_secret.py::test_script_is_executable`: 実行権限は動きの前提として残す

## スコープ外

- 過去の `specs/` と `_dev/` の書き換え（D3）
- CI（`sdd-check.yml`）・`sdd-validate.py`・guard・`sdd_state.py` の動作の変更（スキーマを除く）
- consumer のリポジトリの既存のテストを消すこと（各リポジトリで決める）
- 「AI がマージしない」の変更（#96 で扱う）

## 制約 / 前提

- `rules/` と reviewer の定義・プロンプト・hook のメッセージは英語で命令形・簡潔。`docs/`・テンプレートは日本語（`rules/conventions.md`）
- エージェントに依存しない書き方にする
- 書いた内容を確かめるだけのテストを、この feature で新しく足さない
