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

## superpowers
設計フェーズ（brainstorm/plan）で活用する。Claude Code 専用のため、実装担当の他agentでは使わない。
※ 具体的に使うスキルの対応付けは導入時に確定する（現状は概念レベルで参照）。
