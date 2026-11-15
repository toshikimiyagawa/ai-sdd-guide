"""integration/ci/sdd-board.yml: the repo copy matches the template, and run scripts use no ${{ }} interpolation."""
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "integration" / "ci" / "sdd-board.yml"
REPO_COPY = ROOT / ".github" / "workflows" / "sdd-board.yml"
TEXT = TEMPLATE.read_text()
REPO_TEXT = REPO_COPY.read_text()


def _run_blocks(text: str = None) -> list:
    lines = (TEXT if text is None else text).splitlines()
    blocks = []
    for i, line in enumerate(lines):
        if re.match(r"\s*run: \|\s*$", line):
            indent = len(line) - len(line.lstrip())
            body = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                    break
                body.append(nxt)
            blocks.append("\n".join(body))
    return blocks


def test_repo_copy_matches_template():
    def norm(t):
        keep = [
            l.replace("vendor/ai-sdd-guide/", "")
            for l in t.splitlines()
            if "submodules: true" not in l and "SDD_GUIDE_TOKEN" not in l
        ]
        return [l for l in keep if not l.startswith("# Copy to") and not l.startswith("# and the board") and not l.startswith("# Self-hosted")]

    assert norm(TEXT) == norm(REPO_TEXT)


def test_no_expression_interpolation_in_run_scripts():
    for text in (TEXT, REPO_TEXT):
        blocks = _run_blocks(text)
        assert blocks
        for block in blocks:
            assert "${{" not in block, block
