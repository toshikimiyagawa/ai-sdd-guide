# Issue #53: Issue snapshot CLI + snapshot JSON Schema

## Overview

Implement a machine-checkable Issue snapshot flow for Tier 2 work.

The feature stores the original GitHub Issue body, a SHA-256 digest of that body,
and stable acceptance-condition identifiers in `specs/<feature>/issue-snapshot.json`.
The validator then compares that snapshot with `traceability.json` so Issue ACs
cannot silently disappear between intake, frozen spec, and implementation.

## Source Issue

- Issue: https://github.com/toshikimiyagawa/ai-sdd-guide/issues/53
- Parent: #46
- Tier: 2

## Design Decisions

### Snapshot Location

The generated snapshot belongs to the feature spec directory:

`specs/<feature>/issue-snapshot.json`

This keeps the original Issue evidence next to `spec.md`, `plan.md`, `tasks.md`,
and `traceability.json`.

### Snapshot Schema

Add `orchestration/schema/issue-snapshot.schema.json` with these required fields:

- `issue`: integer Issue number
- `url`: string with `uri` format
- `fetched_at`: ISO 8601 `date-time`
- `raw_body`: exact raw Issue body text stored in the JSON value
- `body_hash`: lowercase 64-character SHA-256 hex digest of `raw_body`
- `stable_acs`: ordered AC entries with `id` and `text`

The schema should reject additional properties at the top level and inside
`stable_acs` entries.

### Stable AC Extraction

The CLI extracts markdown task-list items under the `## 受入条件` section in source
order. It assigns IDs as `<issue>-AC<N>`, starting at 1.

The Issue body itself is not modified. Stability comes from the stored snapshot,
not from editing GitHub.

### CLI Shape

Add a shell entrypoint at `integration/ci/sdd-issue-snapshot.sh`.

For maintainable parsing and tests, the shell entrypoint may delegate to a Python
implementation file in the same directory. The CLI must be able to fetch an Issue
with `gh issue view <N> --json body,title,url` and write:

`specs/<feature>/issue-snapshot.json`

For tests, the implementation should support local body input without requiring
network access.

### Validator Extension

Extend `integration/ci/sdd-validate.py` so Tier 2 validation also checks:

- snapshot file exists and schema-validates
- `sha256(raw_body.encode("utf-8")).hexdigest()` equals `body_hash`
- `stable_acs` IDs exactly match `<issue>-AC<N>` for their order
- each `stable_acs[].id` appears in `traceability.json entries[].issue_ac`
- no traceability entry references an Issue AC absent from the snapshot

Missing, malformed, unreadable, hash-mismatched, or uncheckable snapshots must make
the validator exit non-zero.

## Acceptance Criteria

- [ ] SAC-1: `orchestration/schema/issue-snapshot.schema.json` exists and defines all required fields. (Issue: 53-AC1)
- [ ] SAC-2: snapshot CLI can generate `issue-snapshot.json` from an Issue number. (Issue: 53-AC2)
- [ ] SAC-3: validator detects `body_hash` mismatch against `raw_body` SHA-256 hex digest. (Issue: 53-AC3)
- [ ] SAC-4: `stable_acs[].id` must match `<issue>-AC<N>` in order. (Issue: 53-AC4)
- [ ] SAC-5: validator detects mismatch between `stable_acs` and `traceability.json entries`. (Issue: 53-AC5)
- [ ] SAC-6: validator exits non-zero when an Issue AC is not tracked. (Issue: 53-AC6)
- [ ] SAC-7: validator fails closed when snapshot validation is impossible. (Issue: 53-AC7)

## Out of Scope

- state/tasks schema and the core validator entrypoint, owned by #52
- verification evidence schema and commit SHA checks, owned by #54
- full negative fixture suite, owned by #47
- migration guide, owned by #49

## Subagent Review

Qwen on vLLM reviewed the Issue scope and existing validator/test structure. It
recommended a strict schema, a CLI with deterministic AC extraction, validator
checks for hash and traceability consistency, and negative tests for fail-closed
paths. This design follows those recommendations while keeping the field names
exactly as specified in Issue #53.
