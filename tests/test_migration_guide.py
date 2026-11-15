"""Migration guide presence and content tests."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
GUIDE = ROOT / "docs" / "migration.md"


CI_EXAMPLE = re.compile(r"^bash vendor/ai-sdd-guide/integration/ci/([\w.-]+)\.sh\b(.*)$")


def test_cli_examples_match_cli_options():
    examples = []
    for line in GUIDE.read_text().splitlines():
        m = CI_EXAMPLE.match(line.strip())
        if m:
            examples.append((m.group(1), m.group(2)))
    assert examples, "no bash vendor/ai-sdd-guide/integration/ci/*.sh examples found"
    help_cache = {}
    problems = []
    for name, args in examples:
        sh = ROOT / "integration" / "ci" / f"{name}.sh"
        if not sh.exists():
            problems.append(f"{sh.relative_to(ROOT)} does not exist")
            continue
        if name not in help_cache:
            result = subprocess.run(
                [sys.executable, str(ROOT / "integration" / "ci" / f"{name}.py"), "--help"],
                capture_output=True, text=True, cwd=ROOT,
            )
            assert result.returncode == 0, f"{name}.py --help failed: {result.stderr}"
            help_cache[name] = set(re.findall(r"--[\w-]+", result.stdout))
        for opt in re.findall(r"(?<!\S)--[\w-]+", args):
            if opt not in help_cache[name]:
                problems.append(f"{name}.sh: {opt} not in {name}.py --help")
    assert not problems, problems


SUBMODULE_PATH = re.compile(r"vendor/ai-sdd-guide/([^\s`'\"()]+)")


def test_submodule_paths_exist_in_guide():
    missing = []
    for m in SUBMODULE_PATH.finditer(GUIDE.read_text()):
        path = m.group(1)
        if "<" in path:
            continue
        if path.endswith("..."):
            path = path[:-3]
        path = path.rstrip(".,:;、。）")
        if path and not (ROOT / path).exists():
            missing.append(m.group(0))
    assert not missing, f"vendor/ai-sdd-guide/ paths not found in guide: {missing}"


def _section_body(text, heading):
    start = text.index("\n", text.index("\n" + heading) + 1)
    end = text.find("\n## ", start)
    return text[start:end if end != -1 else len(text)]


def test_step5_describes_actual_sdd_check_steps():
    step5 = _section_body(GUIDE.read_text(), "## 手順 5:")
    yml = (ROOT / "integration" / "ci" / "sdd-check.yml").read_text()
    names = re.findall(r"^\s*- name:\s*(.+?)\s*$", yml, re.MULTILINE)
    assert names, "no step names found in sdd-check.yml"
    missing = [n for n in names if f"**{n}**" not in step5]
    assert not missing, f"手順 5 does not mention sdd-check.yml steps: {missing}"


def test_partial_migration_checklist_lists_existing_schemas():
    body = _section_body(GUIDE.read_text(), "## 部分移行禁止チェックリスト")
    lines = [l for l in body.splitlines() if "`orchestration/schema/`" in l]
    assert len(lines) == 1, f"expected one orchestration/schema/ item: {lines}"
    m = re.search(r"—\s*(.+?)\s+schema\s*$", lines[0])
    assert m, f"cannot parse schema names: {lines[0]}"
    listed = {s.strip() for s in m.group(1).split("/")}
    actual = {p.name[: -len(".schema.json")] for p in (ROOT / "orchestration" / "schema").glob("*.schema.json")}
    assert listed == actual, f"listed {sorted(listed)} != existing {sorted(actual)}"
