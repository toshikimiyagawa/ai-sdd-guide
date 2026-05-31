# 04. Issue トラッカー連携

Issue 登録から SDD ワークフロー完了までを、GitHub / GitLab / Bitbucket / Azure DevOps の
いずれでも同じ流れで回すための連携ルール。agent 向けの正本は `rules/issue-intake.md`。

## ステータスの正本は SDD かんばん

**SDD のステータスの正本は `.sdd/tasks.json`（SDD かんばん）に統一する。** Issue トラッカーが
何であってもステータスの見え方は同じになる。

- 可視化（ターミナル）: `orchestration/tools/kanban.sh`
- 可視化（Web / GitHub Pages）: `integration/ci/kanban-pages.yml`（→ [Issue #18] の成果物）

各プラットフォームのネイティブなボード（GitHub Projects v2 / GitLab・Bitbucket Boards /
Azure Work Items）は**任意の補助ミラー**にすぎない。使いたいプロジェクトだけが張ればよく、
正本は常に `.sdd/tasks.json`。このリポジトリはボードとの双方向同期は行わない。

## プラットフォーム機能マッピング

| 機能 | GitHub | GitLab | Bitbucket | Azure DevOps |
|---|---|---|---|---|
| Tier ラベル（sdd:tier-0/1/2） | Labels | Labels | Labels | Tags / Area |
| Issue 間の依存関係 | Relationships（blocks / blocked by） | Linked issues | Linked issues | Links（Predecessor / Successor） |
| PR との紐付け | `closes #N` | `closes #N` | `closes #N` | `AB#N` |
| **ステータス管理（正本）** | **`.sdd/tasks.json`** | **`.sdd/tasks.json`** | **`.sdd/tasks.json`** | **`.sdd/tasks.json`** |
| ステータス管理（任意ミラー） | Projects v2 | Boards | Boards | Boards / Work Items |

プラットフォームごとに違うのは「ラベル」「依存関係リンク」「PR↔Issue リンク」の3つだけ。
Tier ルールも SDD フェーズも、`.sdd/tasks.json` でのステータス管理も全プラットフォーム共通。

## Issue 登録ルール

**GitHub（基準）:**
- `sdd:tier-0` / `sdd:tier-1` / `sdd:tier-2` ラベルを作成（→ `integration/issue-tracker/labels.sh`）
- 依存関係は Relationship（blocks / blocked by）で登録

**他3プラットフォーム:** 同等の設定方法は `integration/issue-tracker/README.md` を参照。

## Issue → SDD 完了までのフロー

```
Issue 登録（バグ報告・機能要望）
  → 人間が Tier を判断 → sdd:tier-x ラベルを付与
  → エージェントが Issue を読んで SDD ワークフロー開始
     → .sdd/tasks.json にエントリを追加（status = pending）← ステータスの正本
     - Tier 0: そのまま実装 → PR（closes #N）
     - Tier 1: 軽量 spec → 実装 → PR
     - Tier 2: spec → plan → tasks → 実装 → verify → PR
     → フェーズ遷移のたびに .sdd/tasks.json の status を更新
       （in_progress / completed / blocked）
  → PR マージ → tasks.json を完了に更新 → Issue クローズ
```

- Tier の定義は [01. ワークフロー](01-workflow.md) を参照。
- ステータスはフェーズ境界ごとに `.sdd/tasks.json` を更新する（オーケストレーションの
  停止ルールと同じ。`orchestration/rules/orchestration.md`）。これによりかんばんが常に
  現在の状態を表す。
- Tier ラベルは PR にも付ける（hooks / CI が参照。`rules/conventions.md`）。

[Issue #18]: https://github.com/toshikimiyagawa/ai-sdd-guide/issues/18
