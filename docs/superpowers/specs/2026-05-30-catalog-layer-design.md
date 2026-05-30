# Design: System-Wide Catalog Layer

**Date:** 2026-05-30
**Status:** Approved

## 概要

SDDの作業単位（`specs/<feature>/`）とは別に、システム全体を横断する**機能単位カタログ**レイヤーを追加する。画面一覧・API一覧・テーブル一覧などをプロジェクトが自由に定義でき、Claudeが設計フェーズとverifyフェーズで自動更新する。

## アーキテクチャ

### `ai-sdd-guide` 側（新規モジュール）

```
catalog/
  rules/
    catalog.md              # agent向けルール（更新タイミング・手順）
  schema/
    catalog.schema.json     # .sdd/catalog.json のスキーマ
  templates/
    catalog.json.example    # プロジェクト設定例
    index.md.example        # 一覧ファイルの雛形
    definition.md.example   # 個別定義書の雛形
```

既存の `rules/workflow.md` に参照行を1行追記することで、通常のSDDフローに統合する。

### 取り込み側プロジェクト

```
.sdd/catalog.json           # カタログ種類の宣言（プロジェクトが定義）

docs/design/
  screens/
    index.md                # 画面一覧（カタログ）
    SCR-001-login.md        # 個別定義書
    SCR-002-dashboard.md
  apis/
    index.md
    API-001-post-auth-login.md
  tables/
    index.md
    TBL-001-users.md
```

`specs/<feature>/` が「この作業での変更内容」、`docs/design/` が「現時点の最新定義」という役割分担。

## ファイルフォーマット

### `.sdd/catalog.json`

```json
{
  "types": [
    { "id": "screens", "label": "画面一覧",    "id_prefix": "SCR" },
    { "id": "apis",    "label": "API一覧",      "id_prefix": "API" },
    { "id": "tables",  "label": "テーブル一覧", "id_prefix": "TBL" }
  ]
}
```

カタログ種類はフリーフォーム。Webアプリ・バッチ・APIなど系統を問わない。

### `docs/design/<type>/index.md`（一覧）

```markdown
# <label>

| ID | 名称 | ステータス | feature | 定義書 |
|---|---|---|---|---|
| SCR-001 | ログイン画面 | confirmed | [feat-auth](../../specs/feat-auth/spec.md) | [→](SCR-001-login.md) |
| SCR-002 | ダッシュボード | planned | [feat-dashboard](../../specs/feat-dashboard/spec.md) | [→](SCR-002-dashboard.md) |
```

### `docs/design/<type>/<id>.md`（個別定義書）

```markdown
---
id: SCR-001
title: ログイン画面
status: confirmed
feature: feat-auth
updated: YYYY-MM-DD
---

# <id>: <title>

## 概要
（このエントリが表すものの説明）

## 仕様
（プロジェクトに合わせて自由に記述）
```

### ステータス遷移

```
planned  →  confirmed  →  deprecated
（spec時）   （verify時）   （削除・廃止時）
```

`deprecated` はファイルを削除せずステータスだけ変更する（履歴を残す）。

## SDDワークフローへの統合

### 設計フェーズ（spec作成時）

`spec.md` に新しい画面・API・テーブルが登場したら：

1. `.sdd/catalog.json` を読んでカタログ種類を確認する
2. `docs/design/<type>/index.md` に行を追加（status: `planned`、feature: 現在のfeatureスラッグ）
3. `docs/design/<type>/<id>.md` を作成（`## 仕様` セクションは `spec.md` の内容から起こす）

カタログファイルが存在しない場合（プロジェクトがカタログを使っていない）は何もしない。

### verifyフェーズ（実装確認後）

`sdd-reviewer` が実装を確認したら：

1. `index.md` の該当エントリを `planned` → `confirmed` に更新
2. `definition.md` の `updated` 日付と `## 仕様` セクションを実装の実態に合わせて更新（仕様が変わっていた場合）

### 廃止時

spec がエントリの削除を宣言している場合：

1. `index.md` の該当行のステータスを `deprecated` に変更
2. `definition.md` のフロントマターの `status` を `deprecated` に変更

ファイルは削除しない。

### `rules/workflow.md` への追記

既存のワークフロールールに以下の1行を追加：

```
- If .sdd/catalog.json exists: update docs/design/ catalog entries and
  definition files during spec phase (status: planned) and verify phase
  (status: confirmed). See catalog/rules/catalog.md.
```

## スコープ外

- `index.md` の自動生成ツール（定義書ファイルから一覧を再生成するスクリプト）
- カタログ整合性のCI検証（エントリと定義書ファイルの存在チェック）
- テンプレートのカスタマイズ機能

## 未解決事項

なし。
