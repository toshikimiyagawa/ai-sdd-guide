# Spec: traceability-format

- Tier: 2
- Status: frozen
- Feature slug: traceability-format
- Traceability: [traceability.json](traceability.json)

## 背景 / 意図

Issue → spec 変換時に元 Issue の要件が脱落・弱体化する事例（agents-devcontainer PR #54）を防ぐため、
Issue AC → spec AC → task → test の対応を機械検査可能な形式で定義する。

## 受入条件

- [ ] SAC-1: `orchestration/schema/traceability.schema.json` が存在し、全フィールドの型・必須条件・ステータス別バリデーション挙動（in-scope/out-of-scope/deferred）を定義している（元 Issue: 44-AC1）
- [ ] SAC-2: stable AC ID 命名規則（Issue AC = `<issue番号>-AC<連番>`、spec AC = `SAC-<連番>`）が `docs/traceability.md` に記載されており、`templates/spec.md` にも適用されている（元 Issue: 44-AC2）
- [ ] SAC-3: `out-of-scope`/`deferred` エントリには `reason`（空文字不可）と HTTP(S) `followup_issue` が必須であることが schema と docs の両方に明記されている（元 Issue: 44-AC3）
- [ ] SAC-4: `templates/traceability.json.example` が存在し、in-scope・out-of-scope・deferred の3パターンを含み、JSON Schema に対して valid である（元 Issue: 44-AC4）
- [ ] SAC-5: `orchestration/schema/traceability.schema.json` と `templates/traceability.json.example` が後続 validator (#46) の参照に必要な正規パスに存在する（元 Issue: 44-AC5）

## スコープ外

- validator の実装 → #46
- rules ファイルの更新 → #45
- sdd-reviewer / Claude agent の prompt 更新 → #48
- migration guide → #49

## 制約 / 前提

- JSON Schema は draft-07（既存 `orchestration/schema/` と統一）
- feature slug パターン: `^[a-z0-9][a-z0-9-]*$`
- Issue AC ID パターン: `^[0-9]+-AC[0-9]+$`（例: `44-AC1`）
- spec AC ID パターン: `^SAC-[0-9]+$`（例: `SAC-1`）
- task パターン: `^T[0-9]+$`（例: `T1`）
- test パターン: `^.+::.+$`（例: `tests/test_foo.py::test_bar`）
- 1つの Issue AC が複数の spec AC に展開される場合、同じ `issue_ac` を持つエントリを複数記述する（docs/traceability.md 参照）
