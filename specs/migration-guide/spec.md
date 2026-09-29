# Spec: migration-guide

## Intent

ai-sdd-guide の #43 子 issue 群（#44/#45/#52/#53/#54/#48）で実装した変更を consumer repository に適用するための migration guide と update 手順を `docs/migration.md` として作成する。

## Acceptance Criteria

- **SAC-1** — `docs/migration.md` が存在する。
- **SAC-2** — migration guide に全変更項目（traceability, issue snapshot, verification evidence, state/tasks schema, CI validator, hook, reviewer prompt）の適用手順が記載されている。
- **SAC-3** — consumer update チェックリストが migration guide に含まれている。
- **SAC-4** — 新規 feature への全手順適用例と、進行中 feature の変換例が migration guide に含まれている。
- **SAC-5** — 完了済み spec を遡及変更しないことが migration guide に明記されている。
- **SAC-6** — 部分移行を禁止するチェックリストが migration guide に含まれている。
