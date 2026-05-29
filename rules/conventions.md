# Conventions (agent)

## Commits
- One logical change per commit. Reference the feature: `<type>(<feature>): summary`.

## Branches & PRs
- One feature → one branch → one PR. Include `specs/<feature>/` in the PR.
- The PR must carry the Tier label `sdd:tier-{0,1,2}`.

## Code review
- Review for conformance to the frozen spec, not personal preference.
- Out-of-spec changes are rejected, not negotiated in review.
- PR のレビューは `sdd-reviewer` subagent に実施させる。人間のレビュー前に subagent が spec 適合を確認することで、レビュー負荷を下げる。

## Code style
- Follow the host project's existing style. SDD does not override project conventions.
- Default to no comments; explain only a non-obvious "why".
