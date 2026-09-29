# Plan: migration-guide

## Approach

`docs/migration.md` を新規作成する。内容は 7 つの手順セクション＋2 つの具体例＋2 つのチェックリストで構成する。テストは `tests/test_migration_guide.py` でファイル存在・セクション存在・テキストパターンを検査する。

## Affected Files

- Create: `docs/migration.md`
- Create: `tests/test_migration_guide.py`

## Tradeoffs

- 単一ファイル vs `docs/migration/` ディレクトリ: 手順は相互参照が多く読者が一連の流れを追えることが重要なため単一ファイルを選択。
- テスト方針: 文書内容を網羅的に検証するより、各 SAC に 1:1 対応するキーワード/セクション存在テストに絞る。文書の質は review で担保。
