# Handoff: issue-snapshot

## Your scope

Implementation phase only. Do not touch `spec.md`, `plan.md`, or the verify phase.
If the spec needs changes, stop and escalate to a human.

`issue-snapshot.json` is the source Issue evidence for this feature. If the
implementation changes the snapshot CLI output format, stop and escalate instead
of silently rewriting the frozen snapshot contract.

## Done when

- [ ] All tasks in `specs/issue-snapshot/tasks.md` are complete
- [ ] Every acceptance criterion in `specs/issue-snapshot/spec.md` has a passing test
- [ ] Test suite passes

## Reference files

- spec:  `specs/issue-snapshot/spec.md`
- plan:  `specs/issue-snapshot/plan.md`
- tasks: `specs/issue-snapshot/tasks.md`
- traceability: `specs/issue-snapshot/traceability.json`
- issue snapshot: `specs/issue-snapshot/issue-snapshot.json`

## If the spec is ambiguous or insufficient

1. Stop immediately.
2. Set `.sdd/tasks.json` status to `"blocked"`.
3. Fill in `blocked_reason`.
4. Wait for a human to escalate to Claude before resuming.
