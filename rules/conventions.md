# Conventions (agent)

## Commits
- One logical change per commit. Reference the feature: `<type>(<feature>): summary`.

## Branches & PRs
- One feature → one branch → one PR. Include `specs/<feature>/` in the PR.
- The PR must carry the Tier label `sdd:tier-{0,1,2}`.

## Code review
- Review for conformance to the frozen spec, not personal preference.
- Out-of-spec changes are rejected, not negotiated in review.
- Run `sdd-reviewer` before human review. The subagent confirms spec conformance first, reducing reviewer load.

## Code style
- Follow the host project's existing style. SDD does not override project conventions.
- Default to no comments; explain only a non-obvious "why".
