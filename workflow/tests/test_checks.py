"""Unit tests for the deterministic stage checks (run with: python -m pytest workflow/tests)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import checks  # noqa: E402

GOOD = """### FR-01: a
- FR-01-AC1: empty table and count() called → returns 0
- FR-01-AC2 (boundary): three docs and count() called → returns 3
- **FR-01-AC3** (failure): bad input is passed to the function → TypeError is raised
"""


def test_tagged_acs_are_parsed():
    ids = [a for a, _ in checks.parse_acs(GOOD)]
    assert ids == ["FR-01-AC1", "FR-01-AC2", "FR-01-AC3"]
    assert checks.spec_check(GOOD) == []


def test_ac_without_arrow_or_vague_is_rejected():
    bad = "### FR-01: a\n- FR-01-AC1: it should be fast etc.\n"
    problems = checks.spec_check(bad)
    assert any("→" in p for p in problems) and any("vague" in p for p in problems)


def test_requirement_without_acs_is_rejected():
    assert any("FR-02 has no acceptance" in p for p in checks.spec_check(GOOD + "### FR-02: b\n"))


def test_design_check_names_real_and_new_symbols(tmp_path):
    (tmp_path / "tinydb").mkdir()
    (tmp_path / "tinydb" / "a.py").write_text("class Query:\n    def __ne__(self): pass\n")
    ok = "- `tinydb/a.py` :: `Query.__ne__`\n- `tests/test_a.py` :: `test_x` (new)\n"
    assert checks.design_check(ok, tmp_path) == []
    bad = "- `tinydb/a.py` :: `Query.nothing`\n- `setup.py` :: `x`\n"
    assert len(checks.design_check(bad, tmp_path)) == 2


def test_scope_and_coverage_checks():
    design = "- `tinydb/a.py` :: `f`\n"
    assert checks.scope_check(["tinydb/a.py", "tests/x.py"], design) == []
    assert checks.scope_check(["tinydb/b.py"], design) != []
    acs = [("FR-01-AC1", "x"), ("FR-01-AC2", "y")]
    assert checks.ac_coverage_check(acs, "def test_fr_01_ac1_x(): pass") == [
        "No test references FR-01-AC2. Name a test test_fr_01_ac2_<what> or mention the ID in its docstring."]
