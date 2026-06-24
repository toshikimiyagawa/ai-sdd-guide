# Traceability

Tier 2 の spec では、元 Issue の各 AC が spec AC → task → test へ
どう対応するかを `specs/<feature>/traceability.json` に記録する。
validator (#46) がこのファイルを機械検査する。

## 命名規則

### Issue AC ID

```
<issue番号>-AC<連番>
例: 50-AC1, 50-AC2, 100-AC1
```

freeze 前に設計者が元 Issue の各 AC に付ける。
spec.md の受入条件にも同じ ID を付記する:

```markdown
## 受入条件
- [ ] SAC-1: フォームのバリデーションが動作する（元 Issue: 50-AC1）
- [ ] SAC-2: エラーメッセージが表示される（元 Issue: 50-AC2）
```

### spec AC ID

```
SAC-<連番>
例: SAC-1, SAC-2
```

spec.md の受入条件に付ける ID。spec 固有の連番。

## ファイル構造

```json
{
  "issue": <Issue番号>,
  "issue_url": "<Issue URL>",
  "feature": "<feature slug>",
  "entries": [...]
}
```

各エントリの `status` によって必須フィールドが異なる:

| status | 必須フィールド |
|---|---|
| `in-scope` | `spec_ac`, `task`, `test`（すべて非 null） |
| `out-of-scope` | `reason`, `followup_issue` |
| `deferred` | `reason`, `followup_issue` |

## Freeze 前チェックリスト（Tier 2）

1. `specs/<feature>/traceability.json` が存在する
2. `entries` が空でない
3. 元 Issue の全 AC が entries に含まれる（未追跡 AC が 0 件）
4. `out-of-scope` / `deferred` の entries に `reason` と `followup_issue` がある
5. `in-scope` の entries の `spec_ac` / `task` / `test` がすべて非 null

## テンプレート

`templates/traceability.json.example` を参照。
JSON Schema は `orchestration/schema/traceability.schema.json`。
