# Demo video: exact recording script

Total video length **4:45** (limit 5:00). The video is silent: read each line aloud **when its time appears** in the corner of the screen. Calm speaking pace (about 140 words a minute) fits every slide with a second or two to spare. Stay a little under the pace, pause at full stops, and do not rush.

| Time | Scene | On screen | Say (exact words) | Words |
|---|---|---|---|---|
| 0:00 | 1 | One label in, one reviewed pull request out | Imagine reporting a bug on GitHub, adding one label, and minutes later getting a tested, reviewed fix to approve. | 19 (8s of 10s) |
| 0:10 | 1 | Five real issues, each started by one label | I'm Aasritha Kalluri. This is AutoSE, a small team of AI helpers, built on a copy of the open source library tinydb. | 22 (9s of 11s) |
| 0:21 | 2 | A fork pinned to one commit, protected, with a secret key | First, setup. I copied tinydb to my own account and fixed it at one exact version. The main branch is protected, and my API key is stored as a secret. | 30 (13s of 14s) |
| 0:35 | 2 | Reused my A1 skill and A2 architecture; five issues | I reused my skill and architecture document from earlier assignments, and wrote five test issues: two bugs, two features, and one vague request. | 23 (10s of 11s) |
| 0:46 | 2 | Hidden tests stayed private; their hashes came first | I wrote hidden tests to grade fairly, kept them private, and committed their fingerprints first so I could not quietly change them. Spending was capped at five dollars. | 28 (12s of 13s) |
| 0:59 | 3 | ADRs and views were merged before any agent code | Before building anything, I wrote the design. The diagrams and first decision records were merged before any helper code existed. | 20 (9s of 10s) |
| 1:09 | 3 | Three agents, one deterministic orchestrator, a human at the end | Three AI helpers. A Planner turns the issue into a checklist. A Builder writes code and tests. A separate Reviewer checks it. A plain Python program runs the steps, and a human decides the merge. | 35 (15s of 16s) |
| 1:25 | 4 | Six stages: an artifact and a check for each | A run has six steps. After each step, ordinary code, not an AI, checks the output before the next step starts. | 21 (9s of 10s) |
| 1:35 | 4 | The trigger: a real bug report and one label | A real example: a bug report says a not-equal search skips records that lack the field. I add the label autose. | 21 (9s of 10s) |
| 1:45 | 4 | Real log of the run: about three minutes, $0.07 | The Planner wrote twelve requirements. The Builder changed the code and tested each one. Then the program ran the whole test suite itself. | 23 (10s of 11s) |
| 1:56 | 4 | Every stage leaves an artifact | Every step leaves a file behind: requirements, design, code change, and test report. All two hundred forty-two tests passed. | 19 (8s of 10s) |
| 2:06 | 4 | The pull request opens and CI passes | The fix became a pull request, and the automatic checks passed. The Reviewer then looked from a clean copy, seeing only the issue and the change. | 26 (11s of 13s) |
| 2:19 | 4 | The independent review, then a person decides | It ran the tests and its own examples, then approved. About three minutes and seven cents. The pull request stays open; only a person merges. | 25 (11s of 12s) |
| 2:31 | 5 | Hostile input, spending and loops are bounded | Automation needs limits. Only people with write access can start a run, and spending and time are capped. A malicious issue told the helpers to leak secrets; they ignored it. I also forced failures to prove the retries work. | 39 (17s of 18s) |
| 2:49 | 6 | 14 decision records; the highlighted ones are my own decisions | I wrote fourteen decision records. Three were mine: three helpers, one controlling program, and a cheaper model to build with a stronger one to review. | 25 (11s of 12s) |
| 3:01 | 6 | 11 failed attempts, none caused by the agents | Eleven attempts failed along the way, none the AI's fault. They were my plumbing mistakes, including a wrong first restart design, which I replaced. | 24 (10s of 12s) |
| 3:13 | 6 | The vague issue: the pipeline asks the human | For the vague issue, the system no longer guesses. It stops, asks me questions, and continues only after I answer. | 20 (9s of 10s) |
| 3:23 | 7 | One agent vs three: same quality, 70% more cost | Experiment one: do three helpers beat one? Quality was similar, ten of ten against nine of ten, but splitting cost seventy percent more. It also exposed a bug I then fixed. | 31 (13s of 15s) |
| 3:38 | 7 | Independent reviewer: no better at catching defects | Experiment two: does an independent reviewer catch more? On planted bugs, no: eight of ten, against ten of ten for a reviewer that also read the requirements. | 27 (12s of 13s) |
| 3:51 | 7 | A fix was tested against a criterion set in advance | I tried a fix, judged by a rule set beforehand. It wrongly rejected a correct change, so I did not adopt it. | 22 (9s of 11s) |
| 4:02 | 8 | All five issues reached a reviewed pull request | All five issues reached a reviewed pull request for six to nine cents each. Hidden tests pass, except the vague issue missed one extra reading. | 25 (11s of 12s) |
| 4:14 | 8 | Limits and AI use, stated plainly | Honest limits: small samples, costs are my estimates, and I wrote both issues and tests. An AI assistant wrote most code; the decisions and reasons are mine. | 27 (12s of 13s) |
| 4:27 | 9 | What I would change first | If I started again, I would fix saving and restarting progress first, and test it before spending money, since it caused most failures. | 23 (10s of 11s) |
| 4:38 | 9 | Everything is in the repository and the report | Everything is in the repository and the report. Thank you for watching. | 12 (5s of 7s) |

Total narration: **587 words**, about 4.2 minutes at 140 words a minute, inside a 4:45 video.
