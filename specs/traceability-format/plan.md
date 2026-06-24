# Plan: traceability-format

## アプローチ

JSON Schema (draft-07) で traceability.json の構造を定義する。
`in-scope` と `out-of-scope`/`deferred` の2ステータスグループに応じて
if/then/else でバリデーションルールを切り替える。

## 影響ファイル

| Action | Path | 目的 |
|---|---|---|
| Create | `orchestration/schema/traceability.schema.json` | 機械検査可能な JSON Schema |
| Create | `tests/test_traceability_schema.py` | Schema の正しさを検証する pytest テスト |
| Create | `templates/traceability.json.example` | in-scope/out-of-scope/deferred の記入例 |
| Create | `docs/traceability.md` | 命名規則・freeze checklist・記入ガイド |
| Modify | `templates/spec.md` | traceability 参照行・SAC-N 形式を追加 |

## トレードオフ

- JSON Schema draft-07 の if/then/else はシンプルだが、エラーメッセージが不明瞭なことがある。将来 ajv 等への移行も可能。
- task/test の存在チェック（T1 が tasks.md に実在するか）は動的検証が必要なため validator #46 に委譲し、本 issue は形式チェックのみに留める。
- `followup_issue` の HTTPS 制約をスキーマに入れることで、validator #46 が URL を fetch する際のプロトコル保証を schema level で確保する。

## 代替案

- Markdown テーブル: 人間が読みやすいが正規表現パースが壊れやすい → 不採用
- JSON keyed by AC ID: 可変キーで JSON Schema が複雑になる → 不採用
- YAML: 既存ツール（tasks.json, state.json）が JSON のため統一性を優先 → 不採用
