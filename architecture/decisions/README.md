# Architecture decisions (Nygard format)

14 ADRs. The ten required decisions D1 to D10 are ADR-001 to ADR-010; ADR-011 to ADR-014 were written because real runs and experiments showed something. Superseded ADRs are kept; the new one says what was learned.

| ADR | Decision | Chosen | Main rejected option | Main reason | Status |
|---|---|---|---|---|---|
| 001 | D1 Splitting the work | 3 agents (Planner stages 1-2, Builder 3-4, Reviewer 6); release is plain code | one agent for everything; one agent per stage | tool permissions and reviewer independence follow the split; planning is read-only | Accepted, **untested** (Exp 1 could not run: credit exhausted) |
| 002 | D2 Control flow | one Python orchestrator, an explicit state machine | separate Actions jobs triggering each other; an LLM orchestrator | bounded loops and counters, deterministic routing, one concurrency group | Accepted; refined by 012, 013 |
| 003 | D3 Hand-offs | files (artifacts) plus repo access, never transcripts | full transcripts; agent-written summaries | keeps the reviewer independent and prompts small | Accepted |
| 004 | D4 State | artifacts + issue status comment + branch; resume at the first unpassed stage | commit state to the branch; PR comments; cache | visible to humans, survives a cancelled run | **Superseded by 011** (restoring `state.json` did not restore the code) |
| 005 | D5 Tools | SDK tool allowlists per role; GitHub access only in the orchestrator; token stripped from agent environments | GitHub MCP server for agents; unrestricted Bash | a fooled agent can at worst edit the tree and run tests | Accepted (injection test passed; allowlist widened narrowly for `\| tail`) |
| 006 | D6 Models | Haiku for Planner and Builder, Sonnet for the Reviewer | Haiku everywhere; Sonnet everywhere | cost, and a different model for the reviewer | Accepted (Exp 2: Haiku with context matched Sonnet on detection at 1/12 of the cost, so this is not clearly right) |
| 007 | D7 Checks | deterministic code decides every pass/fail; LLMs never grade their own stage | LLM judge per stage | cheap, reproducible, hard to talk around | Accepted; refined by 012 (the AC regex was too strict) |
| 008 | D8 Reviewer independence | fresh context, different model, adversarial prompt, read-and-run but no push; approval without a test run is overruled | same-context reviewer | assignment rule; avoids agreeing with the author | Accepted; Exp 2 did **not** support "independence improves detection" |
| 009 | D9 Safety and failures | hard caps (turns, $0.60/run, retries, timeouts); issue text is untrusted data | provider limit only; a container per agent | predictable worst case; bounded loops | Accepted (cap, concurrency and one injection attack verified; credit exhaustion handled cleanly) |
| 010 | D10 Triggers | label or `/autose` by users with write access; one run per issue, queued | `workflow_dispatch` only; cancel-in-progress; any commenter | cost and write access limited to maintainers; no racing runs | Accepted (outsider refused, second trigger queued: verified) |
| 011 | D4 State (supersedes 004) | restore `state.json`, re-apply `diff.patch`, reuse the open PR, rebase onto the current default branch, newest artifact by `created_at` | fetch the branch from the remote; commit state files | idempotent restarts with preserved budgets | Accepted (three real bugs found and fixed) |
| 012 | D7/D2 Lenient AC parsing and vague issues | accept the skill's tagged criteria; open questions never block a stage | stop and ask; LLM testability judge | a correct spec was rejected by my regex; a vague issue died with an empty diff | AC parsing accepted; the vague-issue rule is superseded by 013 |
| 013 | D2/D10 Ask-the-human gate | `/autose ask` pauses after the spec and posts questions; `/autose go ...` resumes | always ask; LLM decides if the issue is vague | the human owns what the issue means; zero cost while waiting | Accepted (issue #5: same hidden-test score as assuming, cheaper) |
| 014 | D8 Compare with siblings | reviewer compares new code with its closest analogue; reversal of documented behaviour is an `approach` finding | give the reviewer the author's spec | fixes the miss seen in Exp 2 without breaking independence | **Proposed**: pre-registered test partly met (a correct control was rejected twice); production prompt unchanged |

## What the experiments changed in the design
| Evidence | Change |
|---|---|
| First real runs (#3) | ADR-004 superseded by 011: restart restores code, reuses the PR, rebases, takes the newest artifact |
| Run on #4 | ADR-012: the AC parser accepts tagged criteria; unit tests for every check |
| Run on #5 (vague) | ADR-012 then ADR-013: proceed on a stated assumption, or ask the maintainer |
| Budget test | the orchestrator comments on the PR when a run stops after it was opened |
| Injection test | none needed (resisted); allowlist widened narrowly because of benign friction |
| Exp 2 (reviewer independence) | independence kept; ADR-014 proposed; not adopted |
| Exp 1 | not run |

## The three decisions that mattered most (notes for the report)
1. **ADR-002 + 004/011: a deterministic orchestrator with explicit state.** Every hard failure of the real runs was in the plumbing (state, restart, CI, restore), not in the agents; this is also where the design was wrong first.
2. **ADR-008 (+014): reviewer independence.** The only decision tested with a pre-registered experiment; the result is a negative one and says what the independence rule costs.
3. **ADR-007: deterministic checks decide pass/fail.** Stage checks caught real agent errors (design naming a missing symbol, spec without arrows) cheaply, and also produced one false rejection of mine (ADR-012), which unit tests now guard.

## Who decided what (provenance)
The author's own answers in the design discussion: **D1** three agents (1A), **D2** a single Python orchestrator, **D6** Haiku for Planner and Builder and Sonnet for the Reviewer, the choice to test **D1 and D8**, the idea behind **ADR-013** (the human is asked and gives the green flag), the $5 hard limit and the instruction to keep the cost low. Everything else in the ADRs (hand-offs, state, tools, checks, safety numbers, triggers, the follow-up ADRs 011, 012, 014) was proposed by the assistant and accepted by the author, mostly by merging the design pull request (#7) after being asked to read it. The text of every ADR was written by the assistant; each ADR file says in its header who decided what.
