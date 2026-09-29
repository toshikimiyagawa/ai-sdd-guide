## fixture-wrong-state

**再現パターン:** `state.json` の `feature` が `tasks.json` に存在しないfeatureを指している。

**対応チェック:** Check 4 — `check_state_tasks_consistency`

**RED確認コマンド:**
```bash
bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-wrong-state
# → exit 1, stderr に "no matching entry" が含まれる
```
