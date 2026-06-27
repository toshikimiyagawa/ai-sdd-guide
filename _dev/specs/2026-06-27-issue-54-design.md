# Issue #54: Verification evidence JSON Schema + validator validation

## Overview

Define a machine-checkable evidence format for the SDD verify phase and extend
the validator so test evidence cannot be replaced by visual checks, compile-only
checks, or syntax checks with invented test counts.

The feature adds `orchestration/schema/evidence.schema.json` and validator checks
for `specs/<feature>/evidence.json`.

## Source Issue

- Issue: https://github.com/toshikimiyagawa/ai-sdd-guide/issues/54
- Parent: #46
- Grandparent: #43
- Tier: 2

## Design Decisions

### Evidence Location

Verification evidence is stored per feature:

`specs/<feature>/evidence.json`

Unlike `spec.md`, `plan.md`, `tasks.md`, and `traceability.json`, evidence is a
verify-phase artifact. It records the implementation commit and commands executed
after implementation is complete.

### Schema Shape

Add `orchestration/schema/evidence.schema.json` with these required fields:

- `feature`: feature slug
- `commit_sha`: 40-character hexadecimal Git commit/object id
- `entries`: non-empty array of command evidence entries

Each entry requires:

- `command_type`: `test`, `lint`, `build`, or `other`
- `command`: command string
- `result`: stdout/stderr summary or result summary
- `test_count`: integer for `command_type: "test"`, otherwise `null`

The schema rejects additional properties at all levels.

### Test Count Contract

`test_count` is the machine-readable boundary between real test execution and
other verification commands:

- `command_type: "test"` requires a non-negative integer `test_count`.
- `command_type: "lint"`, `"build"`, or `"other"` requires `test_count: null`.

This prevents lint, build, compile, or syntax-only commands from being counted as
tests.

### Validator Behavior

Extend `integration/ci/sdd-validate.py` with `check_evidence(root, feature)`.

For Tier 2 features, the validator checks:

- `specs/<feature>/evidence.json` exists
- evidence schema validation passes
- `commit_sha` exists in the repository via Git

Missing, malformed, schema-invalid, unreadable, or Git-uncheckable evidence must
make the validator exit non-zero. Existing validator conventions can report normal
validation failures as exit 1 and unexpected runtime errors as exit 2.

## Acceptance Criteria

- [ ] SAC-1: `orchestration/schema/evidence.schema.json` exists and defines all required fields. (Issue: 54-AC1)
- [ ] SAC-2: schema validation fails when a non-test entry has non-null `test_count`. (Issue: 54-AC2)
- [ ] SAC-3: schema validation fails when a test entry is missing `test_count`. (Issue: 54-AC3)
- [ ] SAC-4: schema validation fails when `commit_sha` is not 40-character hex. (Issue: 54-AC4)
- [ ] SAC-5: validator checks that `commit_sha` exists in Git. (Issue: 54-AC5)
- [ ] SAC-6: validator fails closed when evidence is missing, broken, or uncheckable. (Issue: 54-AC6)

## Out of Scope

- state/tasks schema and core validator entrypoint, owned by #52
- Issue snapshot generation and Issue AC diff checks, owned by #53
- full negative fixture suite, owned by #47
- migration guide, owned by #49

## Issue Diff Summary

No Issue AC was dropped or scoped out. The frozen spec preserves all six Issue ACs
as SAC-1 through SAC-6.

The design narrows one ambiguous phrase: Issue #54 says `commit_sha` must be
"40 桁 hex". The schema will accept 40 hexadecimal characters without imposing an
extra lowercase-only rule.

## Subagent Review

Qwen on vLLM reviewed the Issue scope and existing validator structure. It
recommended a strict schema, conditional `test_count` constraints, a validator
function for evidence, and focused schema/validator tests. Codex adjusted the draft
to avoid adding an out-of-scope evidence generator and to match the existing
validator exit-code conventions.
