# Architecture decisions (Nygard format)

Author: **Aasritha Kalluri**

14 ADRs. The ten required decisions D1 to D10 are ADR-001 to ADR-010; ADR-011 to ADR-014 were written because real runs and experiments showed something. Superseded ADRs are kept; the new one says what was learned.

| ADR | Decision | Chosen | Main rejected option | Main reason | Status |
|---|---|---|---|---|---|
| 001 | D1 Splitting the work | 3 agents (Planner stages 1-2, Builder 3-4, Reviewer 6); release is plain code | one agent for everything; one agent per stage | tool permissions and reviewer independence follow the split; planning is read-only | Accepted; tested in Exp 1: no quality difference, about 70% more cost per run |
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
| Exp 1 (one agent vs three) | no design change; the split costs about 70% more per run for stages 1-4 with no measured quality gain; exposed a check gap (a listed change need not be applied, an unresolved conflict is reported DONE) |

## The three decisions that mattered most (notes for the report)
1. **ADR-002 + 004/011: a deterministic orchestrator with explicit state.** Every hard failure of the real runs was in the plumbing (state, restart, CI, restore), not in the agents; this is also where the design was wrong first.
2. **ADR-008 (+014): reviewer independence.** The only decision tested with a pre-registered experiment; the result is a negative one and says what the independence rule costs.
3. **ADR-007: deterministic checks decide pass/fail.** Stage checks caught real agent errors (design naming a missing symbol, spec without arrows) cheaply, and also produced one false rejection of mine (ADR-012), which unit tests now guard.

## Who decided what (provenance)
**What I decided directly, and my reasons** (the design discussion and a question-and-answer interview on 2026-11-22):
- the decisions: **D1** three agents (my answer "1A"), **D2** a single Python orchestrator, **D6** Haiku for Planner and Builder and Sonnet for the Reviewer, my choice to test **D1 and D8**, the human gate of **ADR-013**, the $5 hard limit and my instruction to keep the cost low;
- **the reasons** behind ADR-001, 002, 003, 004, 005, 006, 007, 008, 009, 010 and 013: for each, I selected the reasons that are mine from a list and could add my own words. Each of those ADRs has a section "Why (my reasons)" containing exactly the ones I selected (for D6 I did not select cost or Haiku's capability, so neither is given as my reason);
- my note that stage 6 is not purely deterministic (ADR-007), my view after Experiment 2 (ADR-008), and **the lessons I took from the real runs and from the ADR-014 test** (ADR-011, ADR-012, ADR-014).

**Drafted in detail by my coding assistant (Claude Code) and approved by me** (mostly by merging the design pull request #7 after being asked to read it): the mechanisms, numbers and wording. **My coding assistant's response to evidence, reported to me (the lessons are mine):** ADR-011, ADR-012 and ADR-014. The text of the ADRs was written by my coding assistant from my answers above; each ADR header has a "Decided by" line saying who decided what. I read all 14 ADRs and adopted them on 2026-11-22; each carries a "Reviewed and adopted by" line with that date.
