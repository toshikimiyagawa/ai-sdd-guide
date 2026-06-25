from pathlib import Path

ROOT = Path(__file__).parents[1]


def read(path):
    return (ROOT / path).read_text()


# --- core.md ---

def test_core_untracked_ac_stop():
    content = read("rules/core.md")
    assert "every Issue AC must appear in" in content
    assert "STOP — do not freeze and do not implement" in content


def test_core_frozen_artifact_immutable():
    content = read("rules/core.md")
    assert "Frozen artifacts" in content
    assert "only permitted post-freeze edit" in content
    assert "[ ] → [x]" in content
