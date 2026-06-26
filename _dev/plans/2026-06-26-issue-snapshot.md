# Plan: Issue Snapshot

## Goal

Implement Issue #53 by adding a snapshot schema, generation CLI, and Tier 2
validator checks that connect GitHub Issue ACs to `traceability.json`.

## Constraints

- Preserve the exact field names from Issue #53.
- Do not require editing the original GitHub Issue.
- Keep validation fail-closed for missing, malformed, or uncheckable snapshots.
- Keep implementation scoped to snapshot generation and validation. Do not add
  verification evidence behavior from #54.

## Implementation Steps

1. Add `orchestration/schema/issue-snapshot.schema.json`.
   - Require `issue`, `url`, `fetched_at`, `raw_body`, `body_hash`, and
     `stable_acs`.
   - Constrain `body_hash` to lowercase SHA-256 hex.
   - Constrain `stable_acs[].id` to a broad Issue AC pattern at schema level.
   - Reject unknown properties.

2. Add snapshot CLI.
   - Add `integration/ci/sdd-issue-snapshot.sh` as the public entrypoint.
   - Add a Python helper if needed for JSON, hashing, and markdown parsing.
   - Fetch GitHub data with `gh issue view <N> --json body,title,url`.
   - Write `specs/<feature>/issue-snapshot.json`.
   - Support local body input for deterministic tests.

3. Extend `integration/ci/sdd-validate.py`.
   - Load `specs/<feature>/issue-snapshot.json` for active Tier 2 features.
   - Validate it against `issue-snapshot.schema.json`.
   - Compare `body_hash` against SHA-256 of the stored `raw_body`.
   - Check `stable_acs` IDs against exact ordered IDs for `issue`.
   - Compare Issue AC IDs to `traceability.json entries[].issue_ac`.
   - Return validation errors instead of silently skipping snapshot failures.

4. Add focused tests.
   - Schema tests for valid snapshots and invalid IDs/properties.
   - CLI tests using local body input.
   - Validator tests for hash mismatch, AC ID mismatch, traceability mismatch,
     untracked Issue AC, and missing/broken snapshot.

5. Generate/update this feature's own `issue-snapshot.json`.
   - Keep its `body_hash` consistent with the stored `raw_body`.
   - Ensure its `stable_acs` match this feature's `traceability.json`.

## Verification

Run:

```sh
PATH=/tmp/ai-sdd-guide-test-venv/bin:$PATH /tmp/ai-sdd-guide-test-venv/bin/pytest -q
```

Expected result: all tests pass.
