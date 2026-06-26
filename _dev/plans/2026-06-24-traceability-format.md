# Traceability Format Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `orchestration/schema/traceability.schema.json` を中心に、Issue AC → spec AC → task → test の対応を機械検査可能な JSON 形式として定義し、テンプレートとドキュメントを整備する。

**Architecture:** JSON Schema（draft-07）で traceability.json の構造を厳密に定義する。`in-scope` と `out-of-scope`/`deferred` でバリデーションルールを if/then/else で切り替える。テストは pytest + jsonschema ライブラリで schema 自体の正しさを確認する。

**Tech Stack:** JSON Schema draft-07, Python 3, pytest, jsonschema ライブラリ

## Global Constraints

- JSON Schema は `draft-07` を使用する（既存 `orchestration/schema/tasks.schema.json` と統一）
- feature slug パターンは `^[a-z0-9][a-z0-9-]*$`（既存 schema と統一）
- Issue AC ID パターン: `^[0-9]+-AC[0-9]+$`（例: `50-AC1`）
- spec AC ID パターン: `^SAC-[0-9]+$`（例: `SAC-1`）
- テストは `tests/` 配下に配置し `pytest` で実行する
- 計画ファイルの保存先: `_dev/plans/`（CLAUDE.md の設定による）

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `orchestration/schema/traceability.schema.json` | traceability.json の JSON Schema |
| Create | `tests/test_traceability_schema.py` | Schema の正しさを検証する pytest テスト |
| Create | `templates/traceability.json.example` | 記入例テンプレート |
| Create | `docs/traceability.md` | 命名規則・記入ガイド |
| Modify | `templates/spec.md` | traceability.json 参照行を追加 |

---

## Task 1: JSON Schema とテストを作成する（SAC-1, SAC-2, SAC-3）

**Files:**
- Create: `orchestration/schema/traceability.schema.json`
- Create: `tests/test_traceability_schema.py`

**Interfaces:**
- Produces: `SCHEMA_PATH = ROOT / "orchestration/schema/traceability.schema.json"` — Task 2 はこれを参照しないが、#46 の validator がこのパスを使用する

- [ ] **Step 1: jsonschema をインストールする**

```bash
pip install jsonschema
```

Expected: `Successfully installed jsonschema-X.X.X`

- [ ] **Step 2: 失敗するテストを書く**

`tests/test_traceability_schema.py` を新規作成する:

```python
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "orchestration" / "schema" / "traceability.schema.json"


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())


VALID_IN_SCOPE = {
    "issue": 50,
    "issue_url": "https://github.com/owner/repo/issues/50",
    "feature": "form-validation",
    "entries": [
        {
            "issue_ac": "50-AC1",
            "spec_ac": "SAC-1",
            "task": "T1",
            "test": "tests/test_form.py::test_validation",
            "status": "in-scope",
        }
    ],
}

VALID_OUT_OF_SCOPE = {
    "issue": 50,
    "issue_url": "https://github.com/owner/repo/issues/50",
    "feature": "form-validation",
    "entries": [
        {
            "issue_ac": "50-AC1",
            "spec_ac": None,
            "task": None,
            "test": None,
            "status": "out-of-scope",
            "reason": "別 feature で扱う",
            "followup_issue": "https://github.com/owner/repo/issues/51",
        }
    ],
}


def validate(instance, schema):
    jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())


def test_valid_in_scope_passes(schema):
    validate(VALID_IN_SCOPE, schema)


def test_valid_out_of_scope_passes(schema):
    validate(VALID_OUT_OF_SCOPE, schema)


def test_valid_deferred_passes(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                **VALID_OUT_OF_SCOPE["entries"][0],
                "status": "deferred",
            }
        ],
    }
    validate(instance, schema)


def test_in_scope_missing_spec_ac_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": "T1",
                "test": "tests/test_form.py::test_validation",
                "status": "in-scope",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_in_scope_missing_task_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": "SAC-1",
                "task": None,
                "test": "tests/test_form.py::test_validation",
                "status": "in-scope",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_in_scope_missing_test_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": "SAC-1",
                "task": "T1",
                "test": None,
                "status": "in-scope",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_out_of_scope_missing_reason_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": None,
                "test": None,
                "status": "out-of-scope",
                "followup_issue": "https://github.com/owner/repo/issues/51",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_out_of_scope_missing_followup_issue_fails(schema):
    instance = {
        **VALID_OUT_OF_SCOPE,
        "entries": [
            {
                "issue_ac": "50-AC1",
                "spec_ac": None,
                "task": None,
                "test": None,
                "status": "out-of-scope",
                "reason": "別 feature で扱う",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_empty_entries_fails(schema):
    instance = {**VALID_IN_SCOPE, "entries": []}
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_invalid_issue_ac_format_fails(schema):
    instance = {
        **VALID_IN_SCOPE,
        "entries": [
            {
                **VALID_IN_SCOPE["entries"][0],
                "issue_ac": "AC1",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)


def test_missing_issue_url_fails(schema):
    instance = {k: v for k, v in VALID_IN_SCOPE.items() if k != "issue_url"}
    with pytest.raises(jsonschema.ValidationError):
        validate(instance, schema)
```

- [ ] **Step 3: テストが失敗することを確認する**

```bash
cd /path/to/ai-sdd-guide && pytest tests/test_traceability_schema.py -v
```

Expected: `FileNotFoundError` または `FAILED` — schema ファイルが存在しないため失敗する

- [ ] **Step 4: JSON Schema を作成する**

`orchestration/schema/traceability.schema.json` を新規作成する:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SDD Traceability",
  "description": "Issue AC → spec AC → task → test のトレーサビリティテーブル (specs/<feature>/traceability.json)。Tier 2 必須。",
  "type": "object",
  "required": ["issue", "issue_url", "feature", "entries"],
  "additionalProperties": false,
  "properties": {
    "issue": {
      "type": "integer",
      "description": "GitHub Issue 番号"
    },
    "issue_url": {
      "type": "string",
      "format": "uri",
      "description": "Issue の URL"
    },
    "feature": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9-]*$",
      "description": "Feature slug。specs/<feature>/ および state.json の feature と一致する。"
    },
    "entries": {
      "type": "array",
      "minItems": 1,
      "description": "AC トレーサビリティエントリ",
      "items": {
        "type": "object",
        "required": ["issue_ac", "status"],
        "additionalProperties": false,
        "properties": {
          "issue_ac": {
            "type": "string",
            "pattern": "^[0-9]+-AC[0-9]+$",
            "description": "Issue AC ID（<issue番号>-AC<連番> 形式、例: 50-AC1）"
          },
          "spec_ac": {
            "type": ["string", "null"],
            "pattern": "^SAC-[0-9]+$",
            "description": "spec AC ID（SAC-<連番> 形式、例: SAC-1）"
          },
          "task": {
            "type": ["string", "null"],
            "description": "tasks.md のタスク参照（例: T1）"
          },
          "test": {
            "type": ["string", "null"],
            "description": "テスト参照（<ファイル>::<テスト名> 形式）"
          },
          "status": {
            "type": "string",
            "enum": ["in-scope", "out-of-scope", "deferred"],
            "description": "この AC がこの spec のスコープ内かどうか"
          },
          "reason": {
            "type": "string",
            "description": "status が out-of-scope / deferred の場合に必須。scope 外化の理由。"
          },
          "followup_issue": {
            "type": "string",
            "format": "uri",
            "description": "status が out-of-scope / deferred の場合に必須。follow-up Issue URL。"
          }
        },
        "if": {
          "properties": {
            "status": {"const": "in-scope"}
          }
        },
        "then": {
          "required": ["spec_ac", "task", "test"],
          "properties": {
            "spec_ac": {"type": "string"},
            "task": {"type": "string"},
            "test": {"type": "string"}
          }
        },
        "else": {
          "required": ["reason", "followup_issue"]
        }
      }
    }
  }
}
```

- [ ] **Step 5: テストがすべて通ることを確認する**

```bash
pytest tests/test_traceability_schema.py -v
```

Expected output:
```
tests/test_traceability_schema.py::test_valid_in_scope_passes PASSED
tests/test_traceability_schema.py::test_valid_out_of_scope_passes PASSED
tests/test_traceability_schema.py::test_valid_deferred_passes PASSED
tests/test_traceability_schema.py::test_in_scope_missing_spec_ac_fails PASSED
tests/test_traceability_schema.py::test_in_scope_missing_task_fails PASSED
tests/test_traceability_schema.py::test_in_scope_missing_test_fails PASSED
tests/test_traceability_schema.py::test_out_of_scope_missing_reason_fails PASSED
tests/test_traceability_schema.py::test_out_of_scope_missing_followup_issue_fails PASSED
tests/test_traceability_schema.py::test_empty_entries_fails PASSED
tests/test_traceability_schema.py::test_invalid_issue_ac_format_fails PASSED
tests/test_traceability_schema.py::test_missing_issue_url_fails PASSED

11 passed in X.XXs
```

- [ ] **Step 6: コミットする**

```bash
git add orchestration/schema/traceability.schema.json tests/test_traceability_schema.py
git commit -m "feat(traceability): JSON SchemaとSchemaテストを追加する (#44)"
```

---

## Task 2: テンプレート・ドキュメント・spec.md を作成/更新する（SAC-4, SAC-5, SAC-6, SAC-7）

**Files:**
- Create: `templates/traceability.json.example`
- Create: `docs/traceability.md`
- Modify: `templates/spec.md`

**Interfaces:**
- Consumes: `orchestration/schema/traceability.schema.json`（Task 1 で作成）
- Produces: validator (#46) が `orchestration/schema/traceability.schema.json` + `templates/traceability.json.example` を参照できる状態

- [ ] **Step 1: テンプレート例を作成する**

`templates/traceability.json.example` を新規作成する:

```json
{
  "issue": 50,
  "issue_url": "https://github.com/owner/repo/issues/50",
  "feature": "your-feature-slug",
  "entries": [
    {
      "issue_ac": "50-AC1",
      "spec_ac": "SAC-1",
      "task": "T1",
      "test": "tests/test_yourfeature.py::test_acceptance_criterion_1",
      "status": "in-scope"
    },
    {
      "issue_ac": "50-AC2",
      "spec_ac": "SAC-2",
      "task": "T2",
      "test": "tests/test_yourfeature.py::test_acceptance_criterion_2",
      "status": "in-scope"
    },
    {
      "issue_ac": "50-AC3",
      "spec_ac": null,
      "task": null,
      "test": null,
      "status": "out-of-scope",
      "reason": "scope 外化の理由をここに記述する。別 feature / 別 issue で扱う。",
      "followup_issue": "https://github.com/owner/repo/issues/51"
    },
    {
      "issue_ac": "50-AC4",
      "spec_ac": null,
      "task": null,
      "test": null,
      "status": "deferred",
      "reason": "今フェーズでは対応しない理由をここに記述する。",
      "followup_issue": "https://github.com/owner/repo/issues/52"
    }
  ]
}
```

- [ ] **Step 2: ドキュメントを作成する**

`docs/traceability.md` を新規作成する:

```markdown
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
```

- [ ] **Step 3: `templates/spec.md` を更新する**

既存の `templates/spec.md` を開き、ヘッダー部分に traceability 参照行を追加する。

変更前:
```markdown
# Spec: <feature 名>

- Tier: 1 | 2
- Status: draft | frozen
- Feature slug: <feature>
```

変更後:
```markdown
# Spec: <feature 名>

- Tier: 1 | 2
- Status: draft | frozen
- Feature slug: <feature>
- Traceability: [traceability.json](traceability.json) *(Tier 2 必須)*
```

- [ ] **Step 4: 既存テスト + 新規テストをすべて実行する**

```bash
pytest tests/ -v
```

Expected: 全テスト PASS（既存テストへのリグレッションなし）

- [ ] **Step 5: コミットする**

```bash
git add templates/traceability.json.example docs/traceability.md templates/spec.md
git commit -m "feat(traceability): テンプレート・ドキュメント・spec.mdを追加する (#44)"
```

---

## 完了の定義

- [ ] `pytest tests/test_traceability_schema.py` が全 11 件 PASS
- [ ] `pytest tests/` が全件 PASS（リグレッションなし）
- [ ] `orchestration/schema/traceability.schema.json` が存在する
- [ ] `templates/traceability.json.example` が in-scope・out-of-scope・deferred の3パターンを含む
- [ ] `docs/traceability.md` に命名規則・freeze checklist・テンプレート参照が記載されている
- [ ] `templates/spec.md` に traceability 参照行がある
- [ ] sdd-reviewer が PASS（実装フェーズ終了後に確認）
