# 96-ai-merge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 最初の質問のあと、AI が PR のマージと後片付けまで行う流れを guide の既定にする。

**Architecture:** 正本は `orchestration/rules/orchestration.md` に置く（`## Human touchpoints` の 3 を「結果の確認」に、`## Autonomous flow` を 12 手順に、新しい節 `## Merge conditions`・`## Cleanup and report` を足し、`## Escalation conditions` 5 の例外を広げる）。ほかの rules はそこを参照し、「Never merge」を消す。テンプレート・docs は文言だけを合わせる。コードの動作は変えない。

**Tech Stack:** Markdown（rules は英語、docs は日本語）。

**Spec:** `specs/96-ai-merge/spec.md`

## Global Constraints

- `rules/`・`orchestration/rules/`・`integration/AGENTS.md.example`・`orchestration/integration/AGENTS-patch.md.example` は英語で命令形・簡潔。`docs/`・`templates/pr-body.md`・`README.md` は日本語。
- テストは足さない（spec D6。書いた内容を確かめるだけのテストを作らない規約、`rules/core.md`）。
- `docs/migration.md` の過去の版の節・`rules/repo-agent-routing.md`・過去の `specs/`・`_dev/`・CI・validator・guard・`sdd_state.py` は変えない。

## 変更の要点

### `orchestration/rules/orchestration.md`

- `## Human touchpoints`: 冒頭の「Resolve everything else ... carry the work through to the PR.」→「... through merge and cleanup.」。3 を `**Result check**: after the AI merges, cleans up and reports, the human reads the report and the PR's `## AI の判断`. Anything to change becomes a new Issue.` にする。
- `## Autonomous flow`: 8・9 を spec の 8〜12 に置き換える（8 push and create the PR / 9 wait for CI / 10 merge when `## Merge conditions` hold / 11 clean up / 12 report — see `## Cleanup and report`）。
- 新しい節 `## Merge conditions`（`## Autonomous flow` の後）: spec「マージの条件」の 3 条件（Tier 0 は sdd-reviewer を除く）、満たせないときの 3 つの扱い（CI の失敗、main との競合: merge main into the branch, no force push, rerun tests and CI、権限不足: escalate under condition 6, never bypass protection e.g. `--admin`）、マージの方法（squash; if not allowed, an allowed method）。
- 新しい節 `## Cleanup and report`: 後片付けの 4 手順（例: `gh pr merge --squash --delete-branch`、`git worktree remove <path>`、`git branch -D <branch>`、`git switch <default> && git pull --ff-only`）と、ボードはマージで Actions が done にすること。報告の 4 項目と置き場所（present: in the conversation; otherwise comment on the Issue）。
- `## Escalation conditions` 5: 「Pushing the work branch and creating the PR are excluded.」→「Excluded: pushing the work branch, creating the PR, merging it once `## Merge conditions` hold, and deleting the merged work branch and its worktree.」
- `## PR decision log`: 「so the human can check the AI's decisions during PR review」→「so the human can check the AI's decisions after the merge」。

### `rules/core.md`

- `Human touchpoints are limited to the initial question, escalation, and PR review/merge; run every other step autonomously (...). Never merge.` → `Human touchpoints are limited to the initial question and escalation; afterwards the human checks the result. Run every other step autonomously, through merging the PR and cleaning up (`## Merge conditions`, `## Cleanup and report` in `orchestration/rules/orchestration.md`).`

### `rules/workflow.md`

- Step 0: 「After the answer, run the flow autonomously to the PR (`## Autonomous flow`). Never merge.」→「... through merge and cleanup (`## Autonomous flow`).」
- Verify phase の PR の行: 「Report the result to the human, who reviews and merges; never merge.」→「Merge once `## Merge conditions` hold, clean up, and report to the human (`## Cleanup and report`).」CI を待つ文は残す。
- 「The board moves to `done` when the PR is merged.」は残す。

### `rules/issue-intake.md`

- 「The human reviews and merges the PR; never merge.」→「Merge the PR once `## Merge conditions` hold, then clean up and report (`orchestration/rules/orchestration.md`).」

### `rules/conventions.md`

- 「Run `sdd-reviewer` before human review.」→「Run `sdd-reviewer` before merging the PR.」

### テンプレート・例

- `orchestration/templates/handoff.md.example`: マージに触れる記述が無く、新しい流れと矛盾しないので変えない（実装の担当はマージしない。マージはオーケストレーションするエージェントが行う）。

- `templates/pr-body.md`: 「人間が PR レビューで確かめられるように」→「人間がマージの後に確かめられるように」。
- `integration/AGENTS.md.example` の `## Human touchpoints`: 「Humans take part only in the initial question (Tier + spec unknowns), escalation, and PR review/merge. Run every other step autonomously through to the PR; never merge.」→ 最初の質問と問い合わせだけ、マージと後片付けまで自律で進め、人間はマージの後に結果を確かめる（参照する節に Merge conditions・Cleanup and report を足す）。
- `orchestration/integration/AGENTS-patch.md.example`: 冒頭の「and PR review/merge (never merge)」を同じ趣旨に。`### If you are a verify agent` の最後に「wait for CI, merge once Merge conditions hold, clean up and report」を足す。

### docs・README

- `README.md` の `orchestration/rules/orchestration.md` を説明する表の行: 新しい節（マージの条件・後片付けと報告）を足す。
- `README.md:38`: 人間の関与を「最初の質問」「問い合わせ」と「マージの後の結果の確認」にし、「PR の作成まで進める。マージは人間が行う。」→「PR のマージと後片付けまで進める。」
- `docs/00-overview.md`: 「PR のレビューとマージ」「PR の作成まで」を同じ趣旨に。
- `docs/01-workflow.md`: 「人間が関わる場面」の 3 を「結果の確認」に、冒頭の「PR の作成まで」→「PR のマージと後片付けまで」。検証の節の「マージは人間が行う。」→ マージの条件・満たせないときの扱い・後片付け・報告（正本を参照）。
- `docs/02-roles.md` の `## 人間`: 3 を「結果の確認」に。設計担当agent の「PR の作成まで」→「PR のマージと後片付けまで」。
- `docs/03-faq.md`: 「人間はどこで関わる？」の答えを合わせる。Q を 1 つ足す（人間がマージしたいリポジトリは？ → ブランチ保護の必須レビュー。spec D3）。
- `docs/04-issue-tracker.md` のフロー図: 「人間が PR をレビューしてマージ」→「CI とマージの条件を確かめて AI がマージ → 後片付け → 人間に報告」。周りの説明に「PR の作成まで」があれば合わせる。
- `docs/migration.md`: 末尾に spec D5 の節を足す（SAC-6 の 4 項目）。
