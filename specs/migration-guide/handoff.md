# Handoff: migration-guide

## Your scope

Implementation phase only. Do not touch `spec.md`, `plan.md`, or the verify phase.
If the spec needs changes, stop and escalate to a human.

## Done when

- [ ] `docs/migration.md` が存在する
- [ ] `tests/test_migration_guide.py` の 6 テストがすべて PASS する
- [ ] 全テストスイートが PASS する (`pytest tests/ -v`)

## Reference files

- spec:   `specs/migration-guide/spec.md`
- plan:   `specs/migration-guide/plan.md`
- tasks:  `specs/migration-guide/tasks.md`

## Key facts

- 成果物は `docs/migration.md` の 1 ファイル
- テストは `tests/test_migration_guide.py` に作成する（既存テストは変更しない）
- 手順セクション見出しには "手順 N:" プレフィックスを含めること（テストが検査する）
- 遡及変更禁止・部分移行禁止の文言はそれぞれ独立したセクションまたは明示的記述として含めること

## If the spec is ambiguous or insufficient

1. Stop immediately.
2. Set `.sdd/tasks.json` status to `"blocked"`.
3. Fill in `blocked_reason`.
4. Wait for a human to escalate before resuming.
