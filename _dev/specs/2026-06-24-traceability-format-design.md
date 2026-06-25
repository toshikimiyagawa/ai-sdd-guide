# Design: Traceability canonical形式の定義

- Date: 2026-06-24
- Issue: #44 (parent: #43)
- Tier: 2
- Status: draft

## 背景 / 意図

Issue → spec 変換時に元 Issue の要件が脱落・弱体化する問題（agents-devcontainer PR #54）を防ぐため、
Issue AC → spec AC → task → test の対応を機械検査可能な形式で定義する。
本 issue はその canonical 形式（スキーマ・命名規則・テンプレート）の定義のみを扱う。
validator 実装は #46、rules 更新は #45 が担当する。

## 決定事項

| 項目 | 決定 | 理由 |
|---|---|---|
| 配置 | 別ファイル `specs/<feature>/traceability.json` | spec.md をシンプルに保ちつつ validator がパースしやすい |
| フォーマット | JSON（メタデータ付きエンベロープ） | JSON Schema で厳密に検証可能、feature/issue 番号の整合性を自動確認できる |
| Issue AC ID | `<issue番号>-AC<連番>`（例: `50-AC1`） | #N 記法と馴染みやすく、プレフィックスでどの Issue か識別できる |
| 必須 tier | Tier 2 のみ | Tier 1 は軽量 spec のみで十分 |

## ファイル配置

```
specs/<feature>/
  spec.md              # 既存（参照行1行を追加）
  plan.md              # 既存（変更なし）
  tasks.md             # 既存（変更なし）
  traceability.json    # 新規（Tier 2 必須）

orchestration/schema/traceability.schema.json   # JSON Schema（新規）
templates/traceability.json.example             # テンプレート例（新規）
docs/traceability.md                            # 命名規則・記入ガイド（新規）
templates/spec.md                               # 参照行1行追加
```

## JSON Schema 定義

### トップレベル

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `issue` | integer | ✓ | GitHub Issue 番号 |
| `issue_url` | string (uri) | ✓ | Issue の URL |
| `feature` | string | ✓ | feature slug（`state.json` の `feature` と一致） |
| `entries` | array (非空) | ✓ | AC 対応表 |

### entries アイテム

| フィールド | 型 | 必須条件 | 説明 |
|---|---|---|---|
| `issue_ac` | string | 常に必須 | `<issue番号>-AC<連番>` 形式（例: `50-AC1`） |
| `spec_ac` | string \| null | — | spec AC ID（`SAC-<連番>`）または null |
| `task` | string \| null | — | tasks.md のタスク参照（`T1` 等）または null |
| `test` | string \| null | — | `<ファイル>::<テスト名>` または null |
| `status` | enum | 常に必須 | `in-scope` / `out-of-scope` / `deferred` |
| `reason` | string | out-of-scope/deferred 時必須 | scope 外化の理由 |
| `followup_issue` | string (uri) | out-of-scope/deferred 時必須 | follow-up Issue URL |

### バリデーションルール（JSON Schema の if/then で表現）

1. `status: "in-scope"` → `spec_ac`, `task`, `test` はすべて非 null
2. `status: "out-of-scope"` または `"deferred"` → `reason` と `followup_issue` 必須、`spec_ac`/`task`/`test` は null
3. `issue_ac` のプレフィックス（`-AC` 前の数字）が `issue` フィールドの値と一致すること（validator で検証）
4. `entries` は空配列不可

### 整合性チェック（validator #46 が担当）

- `feature` が `state.json` の `feature` と一致すること
- 全 Issue AC が `entries` に含まれること（未追跡 AC 0 件）
- `spec_ac` の重複がないこと
- `task` 参照が `tasks.md` の実在タスクを指すこと
- `test` 参照が実在するテスト識別子であること

## 命名規則

### Issue AC ID

```
<issue番号>-AC<連番>
例: 50-AC1, 50-AC2, 100-AC1
```

設計者が freeze 前に元 Issue の各 AC に ID を付ける。
spec.md の受入条件にも同じ ID を付記して対応を明示する:

```markdown
## 受入条件
- [ ] SAC-1: フォームのバリデーションが動作する（元Issue: 50-AC1）
- [ ] SAC-2: エラーメッセージが表示される（元Issue: 50-AC2）
```

### spec AC ID

```
SAC-<連番>
例: SAC-1, SAC-2
```

spec.md の受入条件に付ける ID。spec 固有の連番。

## 記入例

```json
{
  "issue": 50,
  "issue_url": "https://github.com/owner/repo/issues/50",
  "feature": "form-validation",
  "entries": [
    {
      "issue_ac": "50-AC1",
      "spec_ac": "SAC-1",
      "task": "T1",
      "test": "tests/test_form.py::test_validation",
      "status": "in-scope"
    },
    {
      "issue_ac": "50-AC2",
      "spec_ac": "SAC-2",
      "task": "T2",
      "test": "tests/test_form.py::test_error_message",
      "status": "in-scope"
    },
    {
      "issue_ac": "50-AC3",
      "spec_ac": null,
      "task": null,
      "test": null,
      "status": "out-of-scope",
      "reason": "パフォーマンス要件は別 feature で扱う",
      "followup_issue": "https://github.com/owner/repo/issues/51"
    }
  ]
}
```

## freeze gate への組み込み（#45 が rules に追加）

Tier 2 freeze 前チェックリスト（本 issue が定義、#45 が rules に記述）:

1. `specs/<feature>/traceability.json` が存在する
2. `entries` が空でない
3. すべての Issue AC が entries に含まれる（未追跡 AC が 0 件）
4. `out-of-scope` / `deferred` の entries に `reason` と `followup_issue` がある
5. `in-scope` の entries の `spec_ac` / `task` / `test` がすべて非 null

## 受入条件

- [ ] SAC-1: `orchestration/schema/traceability.schema.json` が存在し、全フィールドの型・必須条件を定義している
- [ ] SAC-2: `in-scope` エントリで `spec_ac`/`task`/`test` が null の場合に JSON Schema バリデーションが失敗する
- [ ] SAC-3: `out-of-scope`/`deferred` エントリで `reason`/`followup_issue` がない場合に JSON Schema バリデーションが失敗する
- [ ] SAC-4: `templates/traceability.json.example` が存在し、in-scope・out-of-scope の両パターンを含む
- [ ] SAC-5: `docs/traceability.md` に命名規則・記入ガイド・サンプルが記載されている
- [ ] SAC-6: `templates/spec.md` に `traceability.json` への参照行が追加されている
- [ ] SAC-7: 後続の validator (#46) が参照できる形式（JSON Schema + サンプル）が整っている

## スコープ外

- validator の実装 → #46
- rules ファイルの更新 → #45
- sdd-reviewer / Claude agent の prompt 更新 → #48
- migration guide → #49
