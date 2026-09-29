# Plan: negative-tests

## Approach

Static fixture directories under `tests/fixtures/fixture-*/` (negative) and `tests/fixtures/fixture-*-valid/` (valid). Each directory is a self-contained SDD repo root passable directly to `--root`. A single new test file `tests/test_negative_fixtures.py` uses subprocess to invoke `sdd-validate.sh` and asserts exit codes + error fragments.

## Affected files

- New: `tests/test_negative_fixtures.py`
- New: `tests/fixtures/fixture-*/` × 14 directories (negative)
- New: `tests/fixtures/fixture-*-valid/` × 14 directories (valid)

## Tradeoffs

- Valid fixtures need real git SHA for evidence.json. Solved by injecting `git rev-parse HEAD` at test time via `tmp_path` copy — same pattern as existing `valid-active/` fixture tests.
- Negative fixtures may fail multiple checks simultaneously; tests assert the specific error fragment is present (not that it's the only error).

## Detail

See `_dev/plans/2026-09-29-negative-fixtures.md` for task-by-task implementation steps with full file contents.
