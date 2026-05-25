# 02. 人とagentの分担

## 人間
- 意図の提示と spec の**承認**（凍結の最終判断）。
- spec が現実と合わない時の意思決定。
- Tier判定が妥当かのチェック。

## Claude（設計担当）
- brainstorm → spec → plan → tasks の作成。
- subagent と superpowers を使った深い検討。
- 実装後の検証（sdd-reviewer）。

## 他のagent（実装担当）
- 凍結 spec を契約として実装。
- 逸脱しない。曖昧なら止めてエスカレーション。

## subagent ロール（Claude・設計/検証のみ）
| ロール | 役割 | 権限 |
|---|---|---|
| researcher | コードベース/先行事例の調査 | 読み取りのみ |
| planner | 承認済specから plan/tasks を起草 | 編集（人間承認前提） |
| sdd-reviewer | 実装の凍結spec適合を監査 | 読み取り＋テスト実行 |

各subagentには会話の文脈が無いので、spec のパスと自己完結したブリーフを渡すこと。

## superpowers（Claude Code 専用プラグイン）
設計フェーズで活用する。実装担当の他agentでは使えないため、成果物 `specs/<feature>/` に落とし込んで橋渡しする。

SDDフェーズと superpowers スキルの対応：

| SDDフェーズ | superpowers スキル | 成果物 |
|---|---|---|
| brainstorm | `brainstorming` | 合意した設計 |
| spec | （brainstorm出力を整形） | `spec.md` |
| plan & tasks | `writing-plans` | `plan.md` / `tasks.md` |
| 実装(Claude時) | `executing-plans` + `test-driven-development` + `systematic-debugging` | コード+テスト |
| 検証 | `verification-before-completion` + `requesting-code-review` | レビュー結果 |
| subagent活用 | `dispatching-parallel-agents` / `subagent-driven-development` | - |

導入は Claude Code のプラグインとして行う（submoduleとは別）：
```
/plugin install superpowers@claude-plugins-official
```
