# 02. 人とagentの分担

## 人間
- 意図の提示と spec の**承認**（凍結の最終判断）。
- spec が現実と合わない時の意思決定。
- Tier判定が妥当かのチェック。

## 設計担当agent（superpowers必須）
- brainstorm → spec → plan → tasks の作成。
- subagent と superpowers を使った深い検討。
- 実装後の検証（sdd-reviewer）。
- Claude Code / Codex CLI / Gemini CLI いずれでも担当可。

## 他のagent（実装担当）
- 凍結 spec を契約として実装。
- 逸脱しない。曖昧なら止めてエスカレーション。

## subagent ロール
| ロール | 役割 | 権限 |
|---|---|---|
| researcher | コードベース/先行事例の調査 | 読み取りのみ |
| planner | 承認済specから plan/tasks を起草 | 編集（人間承認前提） |
| sdd-reviewer | 実装の凍結spec適合を監査 | 読み取り＋テスト実行 |

各subagentには会話の文脈が無いので、spec のパスと自己完結したブリーフを渡すこと。

## superpowers（Claude / Codex / Gemini 対応プラグイン）
設計・検証フェーズで活用する。Claude Code・Codex CLI・Gemini CLI でインストールして使える。成果物 `specs/<feature>/` に設計内容を落とし込み、superpowers を持たないagentへ橋渡しする。

SDDフェーズと superpowers スキルの対応：

| SDDフェーズ | superpowers スキル | 成果物 |
|---|---|---|
| brainstorm | `brainstorming` | 合意した設計 |
| spec | （brainstorm出力を整形） | `spec.md` |
| plan & tasks | `writing-plans` | `plan.md` / `tasks.md` |
| 実装(Claude時) | `executing-plans` + `test-driven-development` + `systematic-debugging` | コード+テスト |
| 検証 | `verification-before-completion` + `requesting-code-review` | レビュー結果 |
| レビュー受領 | `receiving-code-review` | 修正コミット or spec逸脱時のエスカレーション |
| subagent活用 | `dispatching-parallel-agents` / `subagent-driven-development` | - |

導入は Claude Code のプラグインとして行う（submoduleとは別）：
```
/plugin install superpowers@claude-plugins-official
```
