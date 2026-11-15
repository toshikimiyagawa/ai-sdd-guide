# 95-no-content-tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 書いた内容をもう一度確かめるだけのテストを作らない規約を guide の既定にし、受入基準の確かめ方に「差分」を足し、guide 自身の `tests/` から該当するテストを消す。

**Architecture:** 規約の正本は `rules/core.md` の `## Always` に置き、`rules/workflow.md`・`orchestration/rules/orchestration.md`・reviewer の定義とプロンプトはそこを参照する。`traceability.json` は `test` に `"diff"` を許すだけにする（spec D1）。テンプレート・docs・hook のメッセージは文言だけを合わせる。テストの削除は spec の「消すテスト・残すテスト」の表のとおりに行う。

**Tech Stack:** Markdown（rules は英語、docs は日本語）、JSON Schema、bash（hook のメッセージ文字列のみ）、pytest。

**Spec:** `specs/95-no-content-tests/spec.md`

## Global Constraints

- `rules/`・`orchestration/rules/`・`integration/agents/`・`integration/prompts/`・hook のメッセージ・`integration/AGENTS.md.example`・`orchestration/templates/handoff.md.example` は英語で命令形・簡潔。`docs/`・`templates/`（`pr-body.md`・`spec.md`・`tasks.md`）は日本語。
- 書いた内容を確かめるだけのテストを新しく足さない。足すテストは SAC-3 のスキーマと validator の動きを確かめるものだけ。
- 「AI はマージしない」に関わる記述は変えない（#96）。
- CI・`sdd-validate.py`・guard・`sdd_state.py`・過去の `specs/`・`_dev/` は変えない。

## 変更の要点

### `rules/core.md`（`## Always`）

次の 2 行を置き換える。

- `Every acceptance criterion must map to a test. Tests are mandatory for Tier 1+.`

を、次の内容にする（言い回しは周りに合わせてよい）。

- Every acceptance criterion names how it is verified: a passing test, or the diff. Changes to behavior (code, scripts, hooks, schemas) need tests for Tier 1+.
- Verify by the diff, not by a test, any criterion that only states that docs, rules, config, data, templates or wording were written, changed or removed. The reviewer cites the diff lines.
- Never write a test that only re-checks written content: that a doc, rule, config, data file, template or workflow contains (or lacks) a given line, value, phrase, heading or key (order and counts included); that only given lines changed since a fixed commit; or that source code contains a given expression. It guards nothing — the next intended change just breaks it.
- Write tests for behavior: run code, scripts, hooks or CLIs with inputs and check output, exit codes and files; validate data against schemas; mechanical checks that apply to every file of a kind; consistency between artifacts that must agree.

### `rules/workflow.md`

- Design phases 3（Plan & Tasks）: `tasks.md` は「the test proving each acceptance criterion」→「how each acceptance criterion is verified (test or diff; `rules/core.md`)」。
- Implementation phase: `Map every acceptance criterion to a passing test.` → 動きを変える受入基準は通るテストに対応させ、差分で確かめる受入基準にはテストを書かない（`rules/core.md`）。
- Verify phase の sdd-reviewer の項目 6: `Each AC maps to a runnable test, not a manual/visual check.` → テストで確かめる AC は実行できるテスト（目視は不可）に対応し、差分で確かめる AC は reviewer が差分の行を挙げる。差分に書いた内容を確かめるだけのテストがあれば指摘する。

### `orchestration/rules/orchestration.md`（`## Spec review` の Checks）

- `Every spec AC is a checkable statement that maps to a test.` → 各 AC は確かめられる文で、確かめ方（テスト / 差分）が `rules/core.md` に合っている。書いた内容を確かめるだけのテストが計画されていない。
- `Tier 2: ... every AC has a task and a test.` → `every AC has a task and a verification (test or diff)`。

### reviewer

- `integration/agents/spec-reviewer.md`・`integration/prompts/spec-reviewer-prompt.md` の Checks 3・5: 上の orchestration.md と同じ。書いた内容を確かめるだけのテストが計画されていれば `CHANGES`。
- `integration/agents/sdd-reviewer.md`・`integration/prompts/sdd-reviewer-prompt.md`: frontmatter の description（agent のみ）を「every acceptance criterion is verified (test or diff)」に。Steps 3 を「テストで確かめる AC は対応するテストがあって通ること、差分で確かめる AC は満たしている差分の行（`<file>:<line>`）を挙げること」に。項目 6 `Test Coverage` を同じ内容にし、差分に書いた内容を確かめるだけのテストがあれば finding にすることを足す。Report の `missing tests` は動きを変える AC についてのものに。

### `orchestration/schema/traceability.schema.json`

- in-scope（`then`）の `test` の pattern を `^(.+::.+|diff)$` にする。
- `entries[].properties.test.description` を「テスト参照（`<ファイル>::<テスト名>` 形式）。差分で確かめる受入基準は `"diff"`」にする。

### テンプレート・docs・hook

- `templates/spec.md`: 受入条件の説明「各項目は最終的にテストへ対応させる（必須）」→ 各項目に確かめ方（テスト / 差分）を書く。データ・設定・文言を書いたという項目は差分で確かめ、テストにしない。例の行に `確かめ方:` を入れる。
- `templates/tasks.md`: `## テスト（受入条件との対応・必須）` → `## 確かめ方（受入条件との対応・必須）`。例に `AC1 → test: ...` と `AC2 → 差分: <file>` を並べる。完了の定義「全AC対応テストが green」→「テストで確かめる AC のテストが green」。
- `templates/traceability.json.example`: `50-AC2` の `test` を `"diff"` にする（`::` の例は `50-AC1` に残る）。
- `orchestration/templates/handoff.md.example`: `Every acceptance criterion ... has a passing test` → テストで確かめる AC は通るテストがあり、差分で確かめる AC にはテストを書かない。
- `integration/AGENTS.md.example`: `Every acceptance criterion must map to a passing test.` → 同じ趣旨（`vendor/ai-sdd-guide/rules/core.md` を参照）。
- `integration/hooks/codex-skill-reminder.sh` の implement のメッセージ: `every acceptance criterion must map to a passing test` → `verify each acceptance criterion as the spec says (test for behavior, diff for written content); never write tests that only re-check written content`。
- `docs/01-workflow.md`: tasks の説明・実装の「受入条件は必ずテストに対応させる」・検証の節を合わせる。`docs/03-faq.md` に Q を 1 つ足す（なぜ書いた内容を確かめるテストを作らないか、差分でどう確かめるか）。`docs/02-roles.md` の sdd-reviewer の行（「読み取り＋テスト実行」）は変えなくてよいが、受入条件をテストに限る記述があれば合わせる。`README.md` の Tier 1 の行「軽量spec＋テスト」は「軽量spec＋テスト（動きを変えるとき）」にする。
- `docs/migration.md`: 末尾に spec D2 の節を足す（SAC-6 の 5 項目）。

### テストの削除と追加

- spec の「消すテスト・残すテスト」の表のとおり消す。消した関数だけが使っていた補助関数・定数・import・フィクスチャも消す。関数が残らないファイルはファイルごと消す。
- `tests/test_traceability_schema.py` に足す（既存の動かし方に合わせる）:
  - `test_in_scope_test_accepts_diff`: in-scope の項目の `test` が `"diff"` でスキーマを通る
  - `test_in_scope_test_rejects_other_strings`: `"diff2"`・`"tests/test_x.py"`（`::` なし）・`""` が落ちる
- `tests/test_sdd_validate.py` に足す（既存の動かし方に合わせる）:
  - `test_traceability_diff_entry_passes`: `test` が `"diff"` の項目を含む feature で `sdd-validate.py` の traceability の検査がエラーを出さない（テストファイルの存在の検査で落ちない）

## 代替案

- `verification` 欄を足して `test` を任意にする: スキーマ・validator・既存の `traceability.json` すべてに手が入るので採らない（spec D1）。
- `test` を null にする: out-of-scope と区別できなくなるので採らない。
