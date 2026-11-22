"""Deterministic stage checks (ADR-007). No LLM is involved in any pass/fail decision."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

AC_RE = re.compile(r"^\s*[-*]\s*((?:N?FR)-\d+-AC\d+)\s*:\s*(.+?)\s*$", re.M)
REQ_RE = re.compile(r"^#{2,4}\s*((?:N?FR)-\d+)\b", re.M)
BANNED = re.compile(r"\b(etc\.?|and/or|user-friendly|as appropriate)\b|\bfast\b", re.I)
ARROW = ("→", "->")
FILE_LINE_RE = re.compile(r"^\s*[-*]\s*`([^`]+\.py)`\s*::\s*`([^`]+)`(.*)$", re.M)


def parse_acs(spec: str) -> list[tuple[str, str]]:
    return AC_RE.findall(spec)


def spec_check(spec: str) -> list[str]:
    """Stage 1: every acceptance criterion is in `situation -> result` form."""
    problems = []
    acs = parse_acs(spec)
    if not acs:
        return ["No acceptance criteria found. Write them as '- FR-01-AC1: <situation> → <expected result>'."]
    req_ids = set(REQ_RE.findall(spec))
    if not req_ids:
        problems.append("No requirement headings like '### FR-01: title' found.")
    for ac_id, text in acs:
        if not any(a in text for a in ARROW):
            problems.append(f"{ac_id} has no '→' (situation → observable result): {text[:80]}")
        if BANNED.search(text):
            problems.append(f"{ac_id} uses a vague word (etc./and-or/fast/user-friendly/as appropriate).")
        if len(text) < 15:
            problems.append(f"{ac_id} is too short to be testable.")
    for rid in req_ids:
        if not any(a.startswith(rid + "-AC") for a, _ in acs):
            problems.append(f"{rid} has no acceptance criteria.")
    return problems


def parse_design_files(design: str) -> list[tuple[str, str, bool]]:
    """Returns (path, symbol, is_new) from lines like: - `tinydb/queries.py` :: `Query.__ne__`"""
    out = []
    for path, symbol, rest in FILE_LINE_RE.findall(design):
        out.append((path.strip(), symbol.strip(), "(new)" in rest.lower()))
    return out


def design_check(design: str, repo: Path) -> list[str]:
    """Stage 2: the plan names files and functions that exist (or are marked new)."""
    problems = []
    entries = parse_design_files(design)
    if not entries:
        return ["No '## Files to change' entries found. Use lines like: - `tinydb/queries.py` :: `Query.__ne__`"]
    if not any(p.startswith("tinydb/") for p, _, _ in entries):
        problems.append("The plan changes no file under tinydb/.")
    for path, symbol, is_new in entries:
        if not (path.startswith("tinydb/") or path.startswith("tests/")):
            problems.append(f"{path}: only files under tinydb/ and tests/ may be changed.")
            continue
        f = repo / path
        if not f.exists():
            if not is_new:
                problems.append(f"{path} does not exist; mark it '(new)' if it should be created.")
            continue
        name = symbol.split(".")[-1].split("(")[0]
        if not is_new and not re.search(rf"\b(def|class)\s+{re.escape(name)}\b|^{re.escape(name)}\s*=", f.read_text(), re.M):
            problems.append(f"{path}: symbol '{symbol}' not found (mark '(new)' if it is to be added).")
    return problems


def layering_check(repo: Path) -> list[str]:
    """ARCHITECTURE.md constraint 4: dependencies point one way."""
    problems = []
    rules = {
        "tinydb/queries.py": ("table", "database", "storages", "middlewares"),
        "tinydb/storages.py": ("table", "database", "queries", "middlewares", "utils"),
        "tinydb/operations.py": ("table", "database", "queries", "storages", "middlewares", "utils"),
    }
    for rel, banned in rules.items():
        f = repo / rel
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            m = re.match(r"\s*(?:from\s+(?:\.|tinydb\.)(\w+)|from\s+\.\s+import\s+(\w+)|import\s+tinydb\.(\w+))", line)
            if m and (m.group(1) or m.group(2) or m.group(3)) in banned:
                problems.append(f"{rel} must not import {m.group(1) or m.group(2) or m.group(3)} (ARCHITECTURE.md constraint 4).")
    return problems


def build_check(repo: Path) -> list[str]:
    """Stage 3: the code builds (compiles and imports)."""
    r = subprocess.run([sys.executable, "-m", "compileall", "-q", "tinydb"], cwd=repo, capture_output=True, text=True)
    if r.returncode:
        return ["compileall failed:\n" + (r.stdout + r.stderr)[-1500:]]
    r = subprocess.run([sys.executable, "-c", "import tinydb"], cwd=repo, capture_output=True, text=True)
    if r.returncode:
        return ["import tinydb failed:\n" + r.stderr[-1500:]]
    return layering_check(repo)


def scope_check(changed: list[str], design: str) -> list[str]:
    """Stage 3: the diff touches only files named in design.md (plus tests/)."""
    allowed = {p for p, _, _ in parse_design_files(design)}
    extra = [c for c in changed if c not in allowed and not c.startswith("tests/")]
    return [f"Changed file not in design.md: {c}" for c in extra]


def run_pytest(repo: Path, timeout: int = 300) -> tuple[bool, str]:
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov"],
                           cwd=repo, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"pytest timed out after {timeout}s"
    out = (r.stdout + r.stderr)
    return r.returncode == 0, out[-4000:]


def ac_coverage_check(acs: list[tuple[str, str]], test_text: str) -> list[str]:
    """Stage 4: every acceptance criterion ID is referenced by a test (names use _ instead of -)."""
    norm = test_text.lower().replace("-", "_")
    return [f"No test references {a}. Name a test test_{a.lower().replace('-', '_')}_<what> or mention the ID in its docstring."
            for a, _ in acs if a.lower().replace("-", "_") not in norm]
