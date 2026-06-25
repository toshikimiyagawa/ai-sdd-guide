# Design: コア validator — sdd-validate.py + schemas + CI/hook 連携

- Date: 2026-06-26
- Issue: #52 (parent: #46, grandparent: #43)
- Tier: 2
- Status: draft

## 背景 / 意図

#44 で定義した traceability 形式と #45 で追加した freeze/verify ルールを
機械的に強制するコア validator を実装する。CI template と freeze gate hook が
同一スクリプトを呼ぶことで重複実装を排除し、fail-closed を保証する。

## 決定事項

| 項目 | 決定 | 理由 |
|---|---|---|
| 実装言語 | Python 3 | jsonschema ライブラリ導入済み、pytest で直接テスト可能 |
| 構成 | 単一 `sdd-validate.py` + 薄い shell ラッパー | 7検査を1ファイルで管理、#53/#54 は関数追加で拡張 |
| hook 構成 | 新規 `sdd-validate-hook.sh` を追加、`sdd-guard.sh` は変更しない | 責務分離 |
| test 参照チェック | `::` 前のファイルパス存在確認まで（関数名は pytest に任せる） | 適切な分業 |
| skip 機能 | 実装しない | freeze gate / CI からの bypass 経路を排除 |
| 外部依存 | Python stdlib JSON + `git rev-parse` のみ（jq 不要） | 環境依存最小化 |

## ファイル構成

| Action | Path | 役割 |
|---|---|---|
| Create | `orchestration/schema/state.schema.json` | state.json の canonical JSON Schema |
| Modify | `orchestration/schema/tasks.schema.json` | blocked_reason 条件付き必須・assigned_agent 緩和 |
| Create | `integration/ci/sdd-validate.py` | core 7検査実装 |
| Create | `integration/ci/sdd-validate.sh` | python3 sdd-validate.py "$@" ラッパー |
| Create | `integration/hooks/sdd-validate-hook.sh` | freeze gate 用 hook |
| Modify | `integration/ci/sdd-check.yml` | sdd-validate.sh 呼び出しを追加 |
| Create | `tests/test_sdd_validate.py` | pytest ユニットテスト |
| Create | `tests/fixtures/valid-active/` | 正常 active state fixture |
| Create | `tests/fixtures/valid-done/` | 正常 done-reset fixture |
| Create | `tests/fixtures/invalid-state-mismatch/` | state/tasks 不一致 fixture |
| Create | `tests/fixtures/invalid-traceability/` | traceability 異常 fixture |
| Create | `tests/fixtures/invalid-tasks-incomplete/` | phase=verify+未完了 tasks.md fixture |

`templates/sdd-state.schema.json` は削除・移動せず互換用に残す。

## JSON Schema 設計

### `orchestration/schema/state.schema.json`

tier:0 かつ phase:done の reset state のみ feature 省略可。それ以外は必須:

```json
"if": {
  "required": ["tier", "phase"],
  "properties": {
    "tier": { "const": 0 },
    "phase": { "const": "done" }
  }
},
"then": {},
"else": { "required": ["feature"] }
```

フィールド:
- `tier`: integer, enum [0, 1, 2], 常に必須
- `phase`: string, enum [brainstorm, spec, plan, tasks, implement, verify, done], 常に必須
- `feature`: string, pattern `^[a-z0-9][a-z0-9-]*$`, 条件付き必須（上記参照）
- `spec`: string, 任意
- `note`: string, 任意

### `orchestration/schema/tasks.schema.json`（既存を拡張）

- `assigned_agent`: `string | null`（slug pattern `^[a-z][a-z0-9-]*$`）に変更し enum を廃止。consumer 互換を維持しつつ将来拡張を許容。
- `blocked_reason`: `status: "blocked"` のとき `string` 必須かつ `minLength: 1`、それ以外は `null`。if/then/else で表現。

## `sdd-validate.py` 設計

### CLI インターフェース

```
python3 sdd-validate.py [--root <path>] [--feature <slug>]
```

- `--root <path>`: リポジトリルート（省略時は `git rev-parse --show-toplevel`）
- `--feature <slug>`: feature slug（省略時は state.json の `feature` を使用）
- exit 0: 全検査 PASS
- exit 1: validation error（詳細を stderr に出力）
- exit 2: internal error / 検査不能（fail-closed）

### 実行フロー

```
1. root と feature を解決
2. state.json を読み込み、state schema で検証 (check_schema_state)
3. tier=0 かつ phase=done → feature 系チェックをスキップして exit 0
4. tasks.json が存在すれば schema 検証 + feature entry 確認 (check_schema_tasks)
5. Tier 2 active feature: traceability.json を schema 検証 (check_schema_traceability)
6. tasks.json が存在する場合: state/tasks 整合性 (check_state_tasks_consistency)
7. phase=verify の場合: tasks.md 全 checkbox 完了確認 (check_tasks_md_consistency)
8. Tier 2: traceability 内部整合性 (check_traceability_internal)
9. Tier 2: scope-out 検査 (check_scope_out)
```

### 7検査関数

| 関数 | 検査内容 | スキップ条件 |
|---|---|---|
| `check_schema_state(root)` | state.json を state.schema.json で検証 | なし（常時実行） |
| `check_schema_tasks(root)` | tasks.json を tasks.schema.json で検証 + active feature entry 確認 | tasks.json 不存在 |
| `check_schema_traceability(root, feature)` | traceability.json を traceability.schema.json で検証 | Tier 2 以外 / done-reset state |
| `check_state_tasks_consistency(root, feature)` | state.feature/phase と tasks.json entry の一致 | tasks.json 不存在 |
| `check_tasks_md_consistency(root, feature)` | tasks.md の全 checkbox 完了（phase=verify 時） | phase≠verify |
| `check_traceability_internal(root, feature)` | 重複 spec AC ID、存在しない task（T1 等）、存在しないテストファイル | Tier 2 以外 / done-reset state |
| `check_scope_out(root, feature)` | out-of-scope/deferred に reason と HTTP(S) followup_issue | Tier 2 以外 / done-reset state |

### fail-closed

各検査関数は `try/except Exception` で囲み、予期しない例外は exit 2 で報告する。`git rev-parse` 失敗も exit 2。

### traceability 内部整合性の詳細（`check_traceability_internal`）

- **重複 spec AC ID**: entries 内で `spec_ac` が同じ値を持つ行が複数ある場合にエラー
- **存在しない task**: `task` フィールドの値（例: `T1`）が `tasks.md` に `- [x] T1:` または `- [ ] T1:` として存在しない場合にエラー
- **存在しないテストファイル**: `test` フィールドの `::` 前のパスが `root` からの相対パスとして存在しない場合にエラー

## CI/hook 連携

### `sdd-validate.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/sdd-validate.py" "$@"
```

### `sdd-check.yml`（既存に追加）

既存の `sdd:` job に追加:

```yaml
- name: Install dependencies
  run: pip install -e ".[test]"

- name: Run sdd-validate
  run: bash integration/ci/sdd-validate.sh --root .
```

### `sdd-validate-hook.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "${1:-}" = "--root" ]; then
  exec bash "$SCRIPT_DIR/../ci/sdd-validate.sh" "$@"
fi
exec bash "$SCRIPT_DIR/../ci/sdd-validate.sh" \
  --root "$(git rev-parse --show-toplevel)"
```

`sdd-validate-hook.sh` は `--root <path>` を受け取れるようにし、呼び出し側が
consumer repo の root を明示できる形にする。`--root` 未指定時は現在の git
working tree から root を解決する。`git rev-parse` 失敗時は `set -e` により
fail-closed で終了する。

## Fixtures（最小セット）

| Fixture | 内容 | 目的 |
|---|---|---|
| `valid-active/` | tier=2, phase=implement, feature 一致, traceability valid | 正常系 |
| `valid-done/` | tier=0, phase=done, feature なし | schema check 実行、feature 系スキップ |
| `invalid-state-mismatch/` | state.feature="foo", tasks.json に "bar" の entry | state/tasks 不一致検出 |
| `invalid-traceability/` | traceability に重複 spec AC + 存在しないテストファイル | 内部整合性エラー検出 |
| `invalid-tasks-incomplete/` | phase=verify, tasks.md に `- [ ]` が残存 | tasks.md 未完了検出 |

`valid-done/` では `check_schema_state` は実行し、`check_schema_traceability` / `check_traceability_internal` / `check_scope_out` をスキップすることを明示する。

## 受入条件（spec AC）

- [ ] SAC-1: `orchestration/schema/state.schema.json` が active / done-reset の両パターンを定義している（元 Issue: 52-AC1）
- [ ] SAC-2: `orchestration/schema/tasks.schema.json` が全フィールドを定義し、blocked_reason の条件付き必須が schema で表現されている（元 Issue: 52-AC2）
- [ ] SAC-3: `sdd-validate.sh` が python3 sdd-validate.py を呼ぶ薄いラッパーとして存在する（元 Issue: 52-AC3）
- [ ] SAC-4: `sdd-validate.py` が1エントリポイントで core 7検査を実行できる（元 Issue: 52-AC3）
- [ ] SAC-5: CI template (`sdd-check.yml`) が `sdd-validate.sh` を呼んでいる（元 Issue: 52-AC4）
- [ ] SAC-6: `sdd-validate-hook.sh` が freeze gate 用 hook として存在し `sdd-validate.sh` を呼んでいる（元 Issue: 52-AC5）
- [ ] SAC-7: state/tasks 整合性エラーを検出できる（元 Issue: 52-AC6）
- [ ] SAC-8: traceability の schema 違反・重複 spec AC・存在しない task・存在しないテストファイルを検出できる（元 Issue: 52-AC7）
- [ ] SAC-9: scope-out/deferred の followup_issue 欠落を検出できる（元 Issue: 52-AC8相当）
- [ ] SAC-10: fail-open 経路がすべて exit non-zero になる（元 Issue: 52-AC9）
- [ ] SAC-11: active state と done-reset state の両方に互換 fixture がある（元 Issue: 52-AC10）

## スコープ外

- Issue 本文の取得・body hash・stable Issue AC → #53
- Issue 本文 AC と traceability の完全一致検査 → #53
- verification evidence schema / evidence.json 検査 → #54
- PR #54 の網羅的 negative fixtures → #47
