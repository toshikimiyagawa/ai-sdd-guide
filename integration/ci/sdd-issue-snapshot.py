#!/usr/bin/env python3
"""Generate specs/<feature>/issue-snapshot.json from a GitHub Issue."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def extract_stable_acs(raw_body: str, issue: int) -> list[dict[str, str]]:
    """Extract task-list ACs from the `## 受入条件` section."""
    stable_acs: list[dict[str, str]] = []
    in_acceptance_section = False

    for line in raw_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_acceptance_section:
                break
            in_acceptance_section = stripped == "## 受入条件"
            continue

        if not in_acceptance_section:
            continue

        match = re.match(r"^\s*-\s*\[[ xX]\]\s*(.+?)\s*$", line)
        if not match:
            continue

        stable_acs.append({
            "id": f"{issue}-AC{len(stable_acs) + 1}",
            "text": match.group(1),
        })

    return stable_acs


def fetch_issue(issue: int) -> tuple[str, str]:
    result = subprocess.run(
        ["gh", "issue", "view", str(issue), "--json", "body,title,url"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr, end="")
        raise SystemExit(result.returncode)

    data = json.loads(result.stdout)
    return data["body"], data["url"]


def build_snapshot(issue: int, url: str, raw_body: str) -> dict:
    return {
        "issue": issue,
        "url": url,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "raw_body": raw_body,
        "body_hash": hashlib.sha256(raw_body.encode("utf-8")).hexdigest(),
        "stable_acs": extract_stable_acs(raw_body, issue),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SDD issue snapshot")
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--feature", required=True)
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--url")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.body_file:
        if not args.url:
            parser.error("--url is required with --body-file")
        raw_body = args.body_file.read_text(encoding="utf-8")
        url = args.url
    else:
        raw_body, url = fetch_issue(args.issue)

    output = args.output or Path("specs") / args.feature / "issue-snapshot.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_snapshot(args.issue, url, raw_body), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
