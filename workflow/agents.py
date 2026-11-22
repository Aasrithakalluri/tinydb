"""Agent runner: one fresh SDK session per call, per-role tool policy (ADR-005, ADR-009)."""
from __future__ import annotations

import asyncio
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, PermissionResultAllow,
                              PermissionResultDeny, ResultMessage, TextBlock, ToolUseBlock, query)

HAIKU = os.environ.get("AUTOSE_MODEL_FAST", "claude-haiku-5-5")
SONNET = os.environ.get("AUTOSE_MODEL_REVIEWER", "claude-sonnet-5-5")

# role -> (model, built-in tools, max_turns, may_write_dirs, bash_allow)
# only these suffixes are allowed after the command: "2>&1" and a pipe into tail/head with a number (observed harmless in real runs, ADR-005 addendum)
PY_TEST = re.compile(r"python3? -m (pytest|compileall)(?: [^;&|<>`$\n]*?)?(?: 2>&1)?(?: \| (?:tail|head)(?: -n)? ?-?\d+)?")
PY_C = re.compile(r"python3? -c .+", re.S)
PROFILES = {
    "planner": dict(model=HAIKU, tools=["Read", "Grep", "Glob"], max_turns=15, write=(), bash=()),
    "builder": dict(model=HAIKU, tools=["Read", "Grep", "Glob", "Edit", "Write", "Bash"], max_turns=40,
                    write=("tinydb/", "tests/"), bash=(PY_TEST, PY_C)),
    "reviewer": dict(model=SONNET, tools=["Read", "Grep", "Glob", "Bash"], max_turns=25,
                     write=(), bash=(PY_TEST, PY_C)),
    # Experiment 1, variant B only (ADR-001): ONE agent does stages 1-4 in one context, with the Builder's tools
    "single": dict(model=HAIKU, tools=["Read", "Grep", "Glob", "Edit", "Write", "Bash"], max_turns=60,
                   write=("tinydb/", "tests/"), bash=(PY_TEST, PY_C)),
    # Experiment 2, variant B only (ADR-008): a Haiku reviewer that is NOT independent (it also sees the author's artifacts)
    "reviewer_b": dict(model=HAIKU, tools=["Read", "Grep", "Glob", "Bash"], max_turns=25,
                       write=(), bash=(PY_TEST, PY_C)),
}


@dataclass
class AgentResult:
    text: str = ""
    tool_log: list = field(default_factory=list)   # [(tool, input)]
    denied: list = field(default_factory=list)
    cost_usd: float = 0.0
    turns: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""


def _inside(path: str, root: Path) -> Path | None:
    try:
        p = (root / path).resolve() if not os.path.isabs(path) else Path(path).resolve()
        p.relative_to(root.resolve())
        return p
    except Exception:
        return None


def make_policy(role: str, cwd: Path, denied: list):
    prof = PROFILES[role]

    async def can_use_tool(tool_name, tool_input, _ctx):
        def deny(msg):
            denied.append((tool_name, str(tool_input)[:200], msg))
            return PermissionResultDeny(message=msg)

        if tool_name not in prof["tools"]:
            return deny(f"{tool_name} is not available to the {role}.")
        if tool_name in ("Read", "Grep", "Glob"):
            target = tool_input.get("file_path") or tool_input.get("path") or "."
            if _inside(target, cwd) is None:
                return deny("Path outside the working tree.")
            return PermissionResultAllow()
        if tool_name in ("Edit", "Write"):
            p = _inside(tool_input.get("file_path", ""), cwd)
            if p is None or not str(p.relative_to(cwd.resolve())).startswith(prof["write"]):
                return deny(f"You may only edit files under {', '.join(prof['write'])}.")
            return PermissionResultAllow()
        if tool_name == "Bash":
            cmd = tool_input.get("command", "").strip()
            if any(r.fullmatch(cmd) for r in prof["bash"]):
                return PermissionResultAllow()
            return deny("Only 'python -m pytest ...', 'python -m compileall ...' and 'python -c ...' are allowed.")
        return deny("Tool not allowed.")

    return can_use_tool


async def _stream(text: str):
    yield {"type": "user", "message": {"role": "user", "content": text}, "parent_tool_use_id": None, "session_id": "autose"}


async def _run(role: str, system: str, prompt: str, cwd: Path, budget_usd: float, timeout: int) -> AgentResult:
    prof = PROFILES[role]
    res = AgentResult()
    opts = ClaudeAgentOptions(
        model=prof["model"], system_prompt=system, cwd=str(cwd), tools=prof["tools"],
        max_turns=prof["max_turns"], max_budget_usd=max(budget_usd, 0.01),
        can_use_tool=make_policy(role, cwd, res.denied), setting_sources=[],
        permission_mode="default",
    )

    async def go():
        async for m in query(prompt=_stream(prompt), options=opts):
            if isinstance(m, AssistantMessage):
                for b in m.content:
                    if isinstance(b, ToolUseBlock):
                        res.tool_log.append((b.name, b.input))
                    elif isinstance(b, TextBlock):
                        res.text = b.text if not res.text else res.text  # replaced by result below
            elif isinstance(m, ResultMessage):
                res.cost_usd = m.total_cost_usd or 0.0
                res.turns = m.num_turns
                u = m.usage or {}
                res.input_tokens = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                res.output_tokens = u.get("output_tokens", 0)
                res.stop_reason = m.subtype
                if m.result:
                    res.text = m.result

    try:
        await asyncio.wait_for(go(), timeout=timeout)
    except asyncio.TimeoutError:
        res.stop_reason = "timeout"
    return res


def run_agent(role: str, system: str, prompt: str, cwd: Path, budget_usd: float, timeout: int = 900) -> AgentResult:
    return asyncio.run(_run(role, system, prompt, cwd, budget_usd, timeout))
