#!/usr/bin/env python3
"""SDD core validator.

exit 0 = all checks pass
exit 1 = validation error
exit 2 = internal error (fail-closed)
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install -e '.[test]'", file=sys.stderr)
    sys.exit(2)

SCHEMA_DIR = Path(__file__).parent.parent.parent / "orchestration" / "schema"


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read {path}: {exc}") from exc


def _load_schema(name: str) -> dict:
    return _load_json(SCHEMA_DIR / name)


def _validate_schema(instance, schema: dict, label: str) -> list[str]:
    try:
        jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())
        return []
    except jsonschema.ValidationError as exc:
        return [f"{label}: {exc.message}"]


def check_schema_state(root: Path) -> list[str]:
    """Check 1: Validate .sdd/state.json against state.schema.json."""
    state_path = root / ".sdd" / "state.json"
    if not state_path.exists():
        return [f"state.json not found: {state_path}"]
    schema = _load_schema("state.schema.json")
    return _validate_schema(_load_json(state_path), schema, "state.json")


def check_schema_tasks(root: Path, feature: str) -> list[str]:
    """Check 2: Validate .sdd/tasks.json (skip if absent); error if active feature has no entry."""
    tasks_path = root / ".sdd" / "tasks.json"
    if not tasks_path.exists():
        return []
    schema = _load_schema("tasks.schema.json")
    tasks = _load_json(tasks_path)
    errors = _validate_schema(tasks, schema, "tasks.json")
    if errors:
        return errors
    if feature:
        ids = [t.get("id") for t in tasks]
        if feature not in ids:
            errors.append(f"tasks.json: no entry for feature '{feature}'")
    return errors


def check_schema_traceability(root: Path, feature: str) -> list[str]:
    """Check 3: Validate traceability.json (Tier 2 only)."""
    path = root / "specs" / feature / "traceability.json"
    if not path.exists():
        return [f"traceability.json not found: {path}"]
    schema = _load_schema("traceability.schema.json")
    return _validate_schema(_load_json(path), schema, "traceability.json")


def check_state_tasks_consistency(root: Path, feature: str) -> list[str]:
    """Check 4: state.json feature/phase must match the tasks.json entry."""
    tasks_path = root / ".sdd" / "tasks.json"
    if not tasks_path.exists():
        return []
    state = _load_json(root / ".sdd" / "state.json")
    tasks = _load_json(tasks_path)
    state_feature = state.get("feature", "")
    state_phase = state.get("phase", "")
    if not state_feature:
        return []
    entries = {t.get("id"): t for t in tasks if "id" in t}
    if state_feature not in entries:
        return [f"state.json feature='{state_feature}' has no matching entry in tasks.json"]
    entry_phase = entries[state_feature].get("phase", "")
    if entry_phase != state_phase:
        return [
            f"state.json phase='{state_phase}' does not match tasks.json entry"
            f" phase='{entry_phase}' for feature '{state_feature}'"
        ]
    return []


def check_tasks_md_consistency(root: Path, feature: str) -> list[str]:
    """Check 5: For phase=verify, all tasks.md checkboxes must be complete."""
    state = _load_json(root / ".sdd" / "state.json")
    if state.get("phase") != "verify":
        return []
    tasks_md = root / "specs" / feature / "tasks.md"
    if not tasks_md.exists():
        return [f"tasks.md not found: {tasks_md}"]
    errors = []
    for i, line in enumerate(tasks_md.read_text().splitlines(), 1):
        if re.match(r"\s*-\s*\[ \]", line):
            errors.append(f"tasks.md line {i}: unchecked item: {line.strip()}")
    return errors


def check_traceability_internal(root: Path, feature: str) -> list[str]:
    """Check 6: Duplicate spec_ac, task not in tasks.md, test file not found."""
    path = root / "specs" / feature / "traceability.json"
    if not path.exists():
        return [f"traceability.json not found: {path}"]
    data = _load_json(path)
    entries = data.get("entries", [])
    errors = []

    # Duplicate spec_ac
    spec_acs = [e["spec_ac"] for e in entries if e.get("spec_ac")]
    seen: set[str] = set()
    for ac in spec_acs:
        if ac in seen:
            errors.append(f"traceability.json: duplicate spec_ac '{ac}'")
        seen.add(ac)

    # Task references exist in tasks.md
    tasks_md = root / "specs" / feature / "tasks.md"
    in_scope_with_task = [e for e in entries if e.get("task")]
    if in_scope_with_task and not tasks_md.exists():
        errors.append(
            f"traceability.json: tasks.md not found ({tasks_md})"
            " — required to resolve task references"
        )
    elif tasks_md.exists():
        tasks_md_text = tasks_md.read_text()
        for entry in entries:
            task = entry.get("task")
            if task and not re.search(
                rf"[-\s]\[.\]\s+{re.escape(task)}:", tasks_md_text
            ):
                errors.append(
                    f"traceability.json: task '{task}' not found in tasks.md"
                )

    # spec_ac references exist in spec.md
    spec_md = root / "specs" / feature / "spec.md"
    in_scope_with_spec_ac = [e for e in entries if e.get("spec_ac")]
    if in_scope_with_spec_ac and not spec_md.exists():
        errors.append(
            f"traceability.json: spec.md not found ({spec_md})"
            " — required to resolve spec_ac references"
        )
    elif spec_md.exists():
        defined_acs = set(re.findall(r"\bSAC-\d+\b", spec_md.read_text()))
        for entry in entries:
            spec_ac = entry.get("spec_ac")
            if spec_ac and spec_ac not in defined_acs:
                errors.append(
                    f"traceability.json: spec_ac '{spec_ac}' not found in spec.md"
                )

    # Test file existence (path before ::)
    for entry in entries:
        test = entry.get("test")
        if test and "::" in test:
            test_file = test.split("::")[0]
            if not (root / test_file).exists():
                errors.append(
                    f"traceability.json: test file not found: {test_file}"
                )

    return errors


def check_scope_out(root: Path, feature: str) -> list[str]:
    """Check 7: out-of-scope/deferred entries must have reason + HTTP(S) followup_issue."""
    path = root / "specs" / feature / "traceability.json"
    if not path.exists():
        return []
    data = _load_json(path)
    errors = []
    for entry in data.get("entries", []):
        if entry.get("status") in ("out-of-scope", "deferred"):
            ac = entry.get("issue_ac", "?")
            if not entry.get("reason"):
                errors.append(f"traceability.json: {ac} missing reason")
            followup = entry.get("followup_issue", "")
            if not followup or not re.match(r"^https?://", followup):
                errors.append(
                    f"traceability.json: {ac} missing HTTP(S) followup_issue"
                )
    return errors


def check_issue_snapshot(root: Path, feature: str) -> list[str]:
    """Check 8: issue-snapshot.json matches schema, hash, and traceability."""
    snapshot_path = root / "specs" / feature / "issue-snapshot.json"
    if not snapshot_path.exists():
        return [f"issue-snapshot.json not found: {snapshot_path}"]

    errors: list[str] = []
    try:
        snapshot = _load_json(snapshot_path)
    except RuntimeError as exc:
        return [str(exc)]

    errors.extend(
        _validate_schema(
            snapshot,
            _load_schema("issue-snapshot.schema.json"),
            "issue-snapshot.json",
        )
    )
    if errors:
        return errors

    raw_body = snapshot["raw_body"]
    expected_hash = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()
    if snapshot["body_hash"] != expected_hash:
        errors.append(
            "issue-snapshot.json: body_hash does not match raw_body SHA-256 "
            f"(expected {expected_hash}, got {snapshot['body_hash']})"
        )

    issue = snapshot["issue"]
    stable_acs = snapshot.get("stable_acs", [])
    for index, ac in enumerate(stable_acs, 1):
        expected_id = f"{issue}-AC{index}"
        actual_id = ac.get("id")
        if actual_id != expected_id:
            errors.append(
                "issue-snapshot.json: stable_acs "
                f"expected {expected_id}, got {actual_id}"
            )

    traceability_path = root / "specs" / feature / "traceability.json"
    if not traceability_path.exists():
        errors.append(f"traceability.json not found: {traceability_path}")
        return errors

    try:
        traceability = _load_json(traceability_path)
    except RuntimeError as exc:
        errors.append(str(exc))
        return errors

    snapshot_acs = {ac.get("id") for ac in stable_acs if ac.get("id")}
    traceability_acs = {
        entry.get("issue_ac")
        for entry in traceability.get("entries", [])
        if entry.get("issue_ac")
    }

    for issue_ac in sorted(snapshot_acs - traceability_acs):
        errors.append(
            f"issue-snapshot.json: snapshot AC not tracked in traceability.json: {issue_ac}"
        )
    for issue_ac in sorted(traceability_acs - snapshot_acs):
        errors.append(
            f"issue-snapshot.json: traceability AC not in snapshot: {issue_ac}"
        )

    return errors


def check_evidence(root: Path, feature: str) -> list[str]:
    """Check 9: evidence.json matches schema and references an existing commit."""
    evidence_path = root / "specs" / feature / "evidence.json"
    if not evidence_path.exists():
        return [f"evidence.json not found: {evidence_path}"]

    try:
        evidence = _load_json(evidence_path)
    except RuntimeError as exc:
        return [str(exc)]

    errors = _validate_schema(
        evidence,
        _load_schema("evidence.schema.json"),
        "evidence.json",
    )
    if errors:
        return errors

    commit_sha = evidence["commit_sha"]
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{commit_sha}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        root_check = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        if root_check.returncode != 0:
            result = subprocess.run(
                ["git", "-C", str(_resolve_root()), "cat-file", "-e", f"{commit_sha}^{{commit}}"],
                capture_output=True,
                text=True,
                check=False,
            )
    if result.returncode != 0:
        errors.append(
            f"evidence.json: commit_sha not found in git repository: {commit_sha}"
        )

    return errors


def _resolve_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git rev-parse failed: {exc.stderr}", file=sys.stderr)
        sys.exit(2)


def main() -> None:  # noqa: C901
    parser = argparse.ArgumentParser(description="SDD core validator")
    parser.add_argument("--root", type=Path, help="Repository root")
    parser.add_argument("--feature", type=str, help="Feature slug")
    args = parser.parse_args()

    try:
        root = args.root or _resolve_root()
        state_path = root / ".sdd" / "state.json"

        # Check 1: state schema (always)
        errors = check_schema_state(root)
        if errors:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        state = _load_json(state_path)
        tier = state.get("tier", -1)
        phase = state.get("phase", "")

        # done-reset: skip feature checks
        if tier == 0 and phase == "done":
            print("sdd-validate: tier=0 phase=done — feature checks skipped. PASS")
            sys.exit(0)

        feature = args.feature or state.get("feature", "")
        if not feature:
            print("ERROR: no feature in state.json and --feature not provided", file=sys.stderr)
            sys.exit(1)

        all_errors: list[str] = []

        # Check 2: tasks schema
        all_errors.extend(check_schema_tasks(root, feature))

        # Check 3: traceability schema (Tier 2)
        if tier == 2:
            all_errors.extend(check_schema_traceability(root, feature))

        # Check 4: state/tasks consistency
        all_errors.extend(check_state_tasks_consistency(root, feature))

        # Check 5: tasks.md consistency (phase=verify)
        all_errors.extend(check_tasks_md_consistency(root, feature))

        # Check 6: traceability internal (Tier 2)
        if tier == 2:
            all_errors.extend(check_traceability_internal(root, feature))

        # Check 7: scope-out (Tier 2)
        if tier == 2:
            all_errors.extend(check_scope_out(root, feature))

        # Check 8: issue snapshot (Tier 2)
        if tier == 2:
            all_errors.extend(check_issue_snapshot(root, feature))

        # Check 9: evidence (Tier 2)
        if tier == 2:
            all_errors.extend(check_evidence(root, feature))

        if all_errors:
            for e in all_errors:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"sdd-validate: all checks passed for feature '{feature}'")

    except SystemExit:
        raise
    except Exception as exc:  # fail-closed
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
