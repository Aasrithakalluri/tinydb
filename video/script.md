# Demo video: exact recording script

Total video length **4:47** (limit 5:00). The video is silent: read each line aloud **when its time appears** in the corner of the screen. Calm speaking pace (about 135 words a minute) fits every slide with a second or two to spare. Stay a little under the pace, pause at full stops, and do not rush.

| Time | Scene | On screen | Say (exact words) | Words |
|---|---|---|---|---|
| 0:00 | 1 | One label in, one reviewed pull request out | One label on a GitHub issue. A few minutes later, a tested, reviewed pull request is waiting. | 17 (8s of 10s) |
| 0:10 | 1 | Five real issues, each started by one label | I'm Aasritha Kalluri, and this is AutoSE, built on a fork of the tinydb library. | 15 (7s of 9s) |
| 0:19 | 2 | A fork pinned to one commit, protected, with a secret key | I forked tinydb and pinned one commit. Main is protected, and my API key lives in a repository secret. | 19 (8s of 10s) |
| 0:29 | 2 | Reused my A1 skill and A2 architecture; five issues | I reused my requirements skill from assignment one and my architecture document from assignment two, and wrote five issues: two bugs, two features, one vague. | 25 (11s of 13s) |
| 0:42 | 2 | Hidden tests stayed private; their hashes came first | Hidden tests stayed private, with their hashes committed first. Spending was capped at five dollars. | 15 (7s of 9s) |
| 0:51 | 3 | ADRs and views were merged before any agent code | Design came before code: the views and the first decision records were merged before any agent code. | 17 (8s of 10s) |
| 1:01 | 3 | Three agents, one deterministic orchestrator, a human at the end | Three agents: a Planner, a Builder, and an independent Reviewer. One orchestrator decides every step, checks are code, agents never hold the token, and a human merges. | 27 (12s of 14s) |
| 1:15 | 4 | Six stages: an artifact and a check for each | Six stages, each with an artifact and a check before moving on. | 12 (5s of 7s) |
| 1:22 | 4 | The trigger: a real bug report and one label | Here is a real bug: not-equal skips documents missing the field. The maintainer adds the label. | 16 (7s of 9s) |
| 1:31 | 4 | Real log of the run: about three minutes, $0.07 | The Planner writes twelve acceptance criteria. The Builder fixes the code and tests each one. The orchestrator runs the suite itself. | 21 (9s of 11s) |
| 1:42 | 4 | Every stage leaves an artifact | Every stage leaves an artifact: spec, design, diff, and a test report. All 242 tests pass. | 16 (7s of 9s) |
| 1:51 | 4 | The pull request opens and CI passes | A pull request opens and CI passes. The Reviewer then works from a clean checkout, seeing only the issue and the diff. | 22 (10s of 12s) |
| 2:03 | 4 | The independent review, then a person decides | It runs the tests and its own experiments, then approves with evidence. About three minutes, seven cents. The pull request stays open: a person decides. | 25 (11s of 13s) |
| 2:16 | 5 | Hostile input, spending and loops are bounded | Only maintainers can start a run, one run per issue, and hard budget caps stop runaway cost. A real prompt-injection issue, telling agents to leak credentials, was resisted at every stage. Fault-injected tests proved the retry and redesign loops. | 39 (17s of 20s) |
| 2:36 | 6 | 14 decision records; the highlighted ones are my own decisions | I recorded fourteen decisions. Three were mine: three agents, one orchestrator, and Haiku with a stronger, different Sonnet reviewer. | 19 (8s of 11s) |
| 2:47 | 6 | 11 failed attempts, none caused by the agents | Eleven attempts failed along the way, none because of the agents. They were my plumbing, and my first restart design was simply wrong, so I superseded it. | 27 (12s of 14s) |
| 3:01 | 6 | The vague issue: the pipeline asks the human | For the vague issue, the pipeline now asks me, and resumes when I give the green flag. | 17 (8s of 10s) |
| 3:11 | 7 | One agent vs three: same quality, 70% more cost | Experiment one: one agent against three. Same quality, ten of ten against nine of ten, but the split costs seventy percent more. It also exposed a gap: a run reported done while a decision was waiting. | 36 (16s of 18s) |
| 3:29 | 7 | Independent reviewer: no better at catching defects | Experiment two: does an independent reviewer catch more? On seeded defects, no: eight of ten, against ten of ten for a reviewer that also saw the spec. It missed a case the issue never stated. | 35 (16s of 18s) |
| 3:47 | 7 | A fix was tested against a criterion set in advance | My fix was tested against a criterion set beforehand. It falsely rejected a correct change, so it stays unadopted. Negative results are results. | 23 (10s of 12s) |
| 3:59 | 8 | All five issues reached a reviewed pull request | All five issues reached a reviewed pull request for six to nine cents each, and the hidden tests pass; the vague issue misses one extra reading. | 26 (12s of 14s) |
| 4:13 | 8 | Limits and AI use, stated plainly | Limits: small samples, issues and tests written by me, and cost figures that are my own estimates. An AI assistant wrote code and drafted text; the decisions are mine, and that is disclosed. | 33 (15s of 17s) |
| 4:30 | 9 | What I would change first | If I started again, I would fix restart state first, and test it before any paid run. | 17 (8s of 10s) |
| 4:40 | 9 | Everything is in the repository and the report | Everything is in the repository and the report. Thank you. | 10 (4s of 7s) |

Total narration: **529 words**, about 3.9 minutes at 135 words a minute, inside a 4:47 video.
