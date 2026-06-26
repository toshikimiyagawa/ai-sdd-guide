# Handoff: evidence-validation

## Your scope

Implementation phase only. Do not touch `spec.md`, `plan.md`, or the verify phase.
If the spec needs changes, stop and escalate to a human.

`issue-snapshot.json` is the source Issue evidence for this feature. `evidence.json`
is intentionally absent at handoff time; it is created in the verify phase after the
implementation commit exists.

## Done when

- [ ] Implementation tasks in `specs/evidence-validation/tasks.md` are complete
- [ ] Every acceptance criterion in `specs/evidence-validation/spec.md` has a passing test
- [ ] Test suite passes

## Reference files

- spec:  `specs/evidence-validation/spec.md`
- plan:  `specs/evidence-validation/plan.md`
- tasks: `specs/evidence-validation/tasks.md`
- traceability: `specs/evidence-validation/traceability.json`
- issue snapshot: `specs/evidence-validation/issue-snapshot.json`

## If the spec is ambiguous or insufficient

1. Stop immediately.
2. Set `.sdd/tasks.json` status to `"blocked"`.
3. Fill in `blocked_reason`.
4. Wait for a human to escalate before resuming.
