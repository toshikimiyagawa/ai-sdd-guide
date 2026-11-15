# Tasks: 96-ai-merge

> 他 agent が設計コンテキスト無しで実装できるよう、各タスクは具体的に書く。書く内容と共通の制約は plan.md を参照。
> どのタスクも rules・文書・テンプレートを書くだけなので、テストは書かない（`rules/core.md`）。既存のテストが通ったままであることを `uv run --no-project --with pytest --with jsonschema python -m pytest tests -q` で確かめる。タスクごとにコミットする。

## 実装タスク（順序付き）
- [ ] T1: `orchestration/rules/orchestration.md` を書き換える（plan.md: Human touchpoints・Autonomous flow・Merge conditions・Cleanup and report・Escalation conditions 5・PR decision log）。対応AC: SAC-1, SAC-2, SAC-3, SAC-4
- [ ] T2: `rules/core.md`・`rules/workflow.md`・`rules/issue-intake.md`・`rules/conventions.md` を書き換える（plan.md）。対応AC: SAC-1, SAC-2
- [ ] T3: `templates/pr-body.md`・`integration/AGENTS.md.example`・`orchestration/integration/AGENTS-patch.md.example`・`README.md`・`docs/00-overview.md`〜`docs/04-issue-tracker.md` を合わせる（plan.md）。`orchestration/templates/handoff.md.example` は変えない（plan.md）。対応AC: SAC-5
- [ ] T4: `docs/migration.md` の末尾に spec D5 の節を足す（SAC-6 の 4 項目）。対応AC: SAC-6

## 確かめ方（受入条件との対応・必須）
- [ ] SAC-1 → 差分: `rules/core.md`, `rules/workflow.md`, `rules/issue-intake.md`, `rules/conventions.md`, `orchestration/rules/orchestration.md`
- [ ] SAC-2 → 差分: `orchestration/rules/orchestration.md`（`## Merge conditions`）と、そこを参照する rules
- [ ] SAC-3 → 差分: `orchestration/rules/orchestration.md`（`## Cleanup and report`）
- [ ] SAC-4 → 差分: `orchestration/rules/orchestration.md`（`## Escalation conditions` 5）
- [ ] SAC-5 → 差分: T3 のファイル
- [ ] SAC-6 → 差分: `docs/migration.md`

## 完了の定義
- 既存のテストが green（`uv run --no-project --with pytest --with jsonschema python -m pytest tests -q`）
- `uv run -q --no-project --with jsonschema python integration/ci/sdd-validate.py --root . --pr --pr-labels sdd:tier-2` が PASS（`evidence.json` は verify で作る）
- CI green / sdd-reviewer 合格（verify フェーズで確認）
（上のチェック欄はすべて `[x]` にしてから verify へ進む。この「完了の定義」はチェック欄にしない）
