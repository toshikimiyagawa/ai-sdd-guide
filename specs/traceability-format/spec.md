# Spec: traceability-format

- Tier: 2
- Status: frozen
- Feature slug: traceability-format
- Traceability: [traceability.json](traceability.json)

## 背景 / 意図

Issue → spec 変換時に元 Issue の要件が脱落・弱体化する事例（agents-devcontainer PR #54）を防ぐため、
Issue AC → spec AC → task → test の対応を機械検査可能な形式で定義する。

## 受入条件

- [ ] SAC-1: `orchestration/schema/traceability.schema.json` が存在し、全フィールドの型・必須条件を定義している（元 Issue: 44-AC1）
- [ ] SAC-2: `in-scope` エントリで `spec_ac`/`task`/`test` が null または非 `T<N>`/`file::test` 形式の場合に JSON Schema バリデーションが失敗する（元 Issue: 44-AC2）
- [ ] SAC-3: `out-of-scope`/`deferred` エントリで `reason`/`followup_issue` がない・空・非 HTTP(S) URL の場合、または `spec_ac`/`task`/`test` が非 null の場合に JSON Schema バリデーションが失敗する（元 Issue: 44-AC3）
- [ ] SAC-4: `templates/traceability.json.example` が存在し、in-scope・out-of-scope・deferred の3パターンを含む（元 Issue: 44-AC4）
- [ ] SAC-5: `docs/traceability.md` に命名規則・記入ガイド・サンプルが記載されている（元 Issue: 44-AC5）
- [ ] SAC-6: `templates/spec.md` に `traceability.json` への参照行が追加され、spec AC ID が `SAC-N` 形式で統一されている（元 Issue: 44-AC6）
- [ ] SAC-7: 後続の validator (#46) が参照できる形式（JSON Schema + サンプル）が整っている（元 Issue: 44-AC7）

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
