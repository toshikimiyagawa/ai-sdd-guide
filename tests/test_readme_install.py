"""README install steps (導入手順) tests: optional board step and workflow set."""
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
README = ROOT / "README.md"
UPDATE_SH = ROOT / "integration" / "update.sh"
HEADING = "## 導入手順（取り込み側プロジェクト）"


def install_section() -> str:
    text = README.read_text(encoding="utf-8")
    start = text.index(HEADING)
    rest = text[start + len(HEADING):]
    m = re.search(r"^## ", rest, re.MULTILINE)
    return rest[: m.start()] if m else rest


def test_install_workflows_match_update_sh():
    update_set = set(re.findall(r'cp "\$INTEGRATION/ci/([\w.-]+\.yml)"', UPDATE_SH.read_text(encoding="utf-8")))
    readme_set = set(re.findall(
        r"cp vendor/ai-sdd-guide/integration/ci/([\w.-]+\.yml) \.github/workflows/", install_section()))
    assert update_set, "update.sh からワークフローのコピーを読み取れない"
    assert readme_set == update_set, \
        f"導入手順のワークフロー {sorted(readme_set)} と update.sh の {sorted(update_set)} が一致しない"
