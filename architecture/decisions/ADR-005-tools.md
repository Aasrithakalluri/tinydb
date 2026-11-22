# ADR-005: Least-privilege tools via SDK allowlists; GitHub access only in the orchestrator

- **Decision area:** D5 Tools
- **Status:** Accepted

## Context
Agents read untrusted issue text and run code in a CI runner that holds secrets. The strongest safeguard is that an agent cannot do harm even when fooled.

## Decision
Agents are run with the Claude Agent SDK. Tools are granted per agent by `allowed_tools` and a Bash command allowlist:

| Agent | Tools |
|-------|-------|
| Planner | `Read`, `Grep`, `Glob` (no write, no Bash, no network) |
| Builder | `Read`, `Grep`, `Glob`, `Edit`, `Write` (inside the working tree), `Bash` limited to `python -m pytest`, `python -m compileall`, `python -c` |
| Reviewer | `Read`, `Grep`, `Glob`, `Bash` limited to `python -m pytest`, `python -c`; no `Edit`/`Write` outside a scratch dir |

No agent gets `WebFetch`/MCP servers (the A1 skill's optional fetch tool is disabled here: not needed for code tasks and a prompt-injection channel). GitHub operations (clone, push, `gh pr create`, comments) are plain code in the orchestrator via the `gh` CLI. Agent subprocesses get a **stripped environment**: `ANTHROPIC_API_KEY` yes, `GITHUB_TOKEN` no; checkout uses `persist-credentials: false` so no token sits in `.git/config`.

## Alternatives considered
- **GitHub MCP server for agents:** convenient, but gives agents write access to GitHub and a bigger tool surface.
- **Unrestricted Bash:** simplest, but a fooled agent could exfiltrate secrets or push.

## Consequences
+ A prompt-injected agent can at worst edit the working tree and run tests.
− Allowlisted Bash is limiting (no `git diff`, no pip); the orchestrator produces diffs for agents.
− Allowlist enforcement depends on the SDK; a Python `-c` call can still run arbitrary Python in the runner (residual risk, no secrets in env mitigates; listed in Limitations).

## Addendum 2026-11-22: allowlist friction observed
In the injection run the Builder and Reviewer made 5 denied calls, all benign (`&& echo OK`, `| tail -5`, a heredoc). They cost turns and retries but no attack was involved. The allowlist now also accepts exactly one suffix, `2>&1` and a pipe into `tail` or `head` with a number; `;`, `&&`, `|` into anything else, redirections and substitutions stay blocked (30 workflow tests, including 9 rejection cases). The denied calls are recorded in `state.json` (`denied_calls`) so the friction can be measured instead of guessed.
