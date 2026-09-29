## fixture-phase-mismatch

**再現パターン:** `state.json` の `phase` と `tasks.json` エントリの `phase` が不一致。

**対応チェック:** Check 4 — `check_state_tasks_consistency`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-phase-mismatch
# → exit 1, stderr に "does not match tasks.json entry" が含まれる
```
