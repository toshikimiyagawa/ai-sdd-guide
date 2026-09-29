## fixture-missing-tasks-entry

**再現パターン:** `tasks.json` が空で active feature のエントリがない。

**対応チェック:** Check 2 — `check_schema_tasks`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-missing-tasks-entry
# → exit 1, stderr に "no entry for feature" が含まれる
```
