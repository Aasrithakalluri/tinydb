# Demo video: exact recording script

Total video length **4:56** (limit 5:00). The video is silent: read each line aloud **when its time appears** in the corner of the screen. Calm speaking pace (about 140 words a minute) fits every slide with a second or two to spare. Stay a little under the pace, pause at full stops, and do not rush.

| Time | Scene | On screen | Say (exact words) | Words |
|---|---|---|---|---|
| 0:00 | 1 | One label in, one reviewed pull request out | Hi, I'm Aasritha Kalluri. In this video I'll show how I built a small AI team that fixes a software bug, from start to finish. | 25 (11s of 12s) |
| 0:12 | 1 | Five real issues, each started by one label | It's called AutoSE. You add one label to a bug report, and a few minutes later a tested fix is waiting for you to review. I built it on a copy of the library tinydb. | 35 (15s of 16s) |
| 0:28 | 2 | A fork pinned to one commit, protected, with a secret key | First, setup. I copied tinydb to my own account and fixed it at one exact version. The main branch is protected, and my API key is stored as a secret. | 30 (13s of 14s) |
| 0:42 | 2 | Reused my A1 skill and A2 architecture; five issues | I reused my skill and architecture document from earlier assignments, and wrote five test issues: two bugs, two features, and one vague request. | 23 (10s of 11s) |
| 0:53 | 2 | Hidden tests stayed private; their hashes came first | I wrote hidden tests to grade fairly, kept them private, and committed their fingerprints first so I could not quietly change them. Spending was capped at five dollars. | 28 (12s of 13s) |
| 1:06 | 3 | ADRs and views were merged before any agent code | Before building anything, I wrote the design. The diagrams and first decision records were merged before any helper code existed. | 20 (9s of 10s) |
| 1:16 | 3 | Three agents, one deterministic orchestrator, a human at the end | Three AI helpers. A Planner turns the issue into a checklist. A Builder writes code and tests. A separate Reviewer checks it. A plain Python program runs the steps, and a human decides the merge. | 35 (15s of 16s) |
| 1:32 | 4 | Six stages: an artifact and a check for each | A run has six steps. After each step, ordinary code, not an AI, checks the output before the next step starts. | 21 (9s of 10s) |
| 1:42 | 4 | The trigger: a real bug report and one label | A real example: a bug report says a not-equal search skips records that lack the field. I add the label autose. | 21 (9s of 10s) |
| 1:52 | 4 | Real log of the run: about three minutes, $0.07 | The Planner wrote twelve requirements. The Builder changed the code and tested each one. Then the program ran the whole test suite itself. | 23 (10s of 11s) |
| 2:03 | 4 | Every stage leaves an artifact | Every step leaves a file behind: requirements, design, code change, and test report. All two hundred forty-two tests passed. | 19 (8s of 10s) |
| 2:13 | 4 | The pull request opens and CI passes | The fix became a pull request, and the automatic checks passed. The Reviewer then looked from a clean copy, seeing only the issue and the change. | 26 (11s of 13s) |
| 2:26 | 4 | The independent review, then a person decides | It ran the tests and its own examples, then approved. About three minutes and seven cents. The pull request stays open; only a person merges. | 25 (11s of 12s) |
| 2:38 | 5 | Hostile input, spending and loops are bounded | Automation needs limits. Only people with write access can start a run, and spending and time are capped. A malicious issue told the helpers to leak secrets; they ignored it. I also forced failures to prove the retries work. | 39 (17s of 18s) |
| 2:56 | 6 | 14 decision records, all written and reviewed by me; highlighted: the biggest choices | I wrote and reviewed all fourteen decision records, each giving the reasons for a choice. The biggest were three helpers, one controlling program, and a cheaper model to build with a stronger one to review. | 35 (15s of 16s) |
| 3:12 | 6 | 11 failed attempts, none caused by the agents | Eleven attempts failed along the way, none the AI's fault. They were my plumbing mistakes, including a wrong first restart design, which I replaced. | 24 (10s of 12s) |
| 3:24 | 6 | The vague issue: the pipeline asks the human | For the vague issue, the system no longer guesses. It stops, asks me questions, and continues only after I answer. | 20 (9s of 10s) |
| 3:34 | 7 | One agent vs three: same quality, 70% more cost | Experiment one: do three helpers beat one? Quality was similar, ten of ten against nine of ten, but splitting cost seventy percent more. It also exposed a bug I then fixed. | 31 (13s of 15s) |
| 3:49 | 7 | Independent reviewer: no better at catching defects | Experiment two: does an independent reviewer catch more? On planted bugs, no: eight of ten, against ten of ten for a reviewer that also read the requirements. | 27 (12s of 13s) |
| 4:02 | 7 | A fix was tested against a criterion set in advance | I tried a fix, judged by a rule set beforehand. It wrongly rejected a correct change, so I did not adopt it. | 22 (9s of 11s) |
| 4:13 | 8 | All five issues reached a reviewed pull request | All five issues reached a reviewed pull request for six to nine cents each. Hidden tests pass, except the vague issue missed one extra reading. | 25 (11s of 12s) |
| 4:25 | 8 | Limits and AI use, stated plainly | Honest limits: small samples, costs are my estimates, and I wrote both issues and tests. An AI assistant wrote most code; the decisions and reasons are mine. | 27 (12s of 13s) |
| 4:38 | 9 | What I would change first | If I started again, I would fix saving and restarting progress first, and test it before spending money, since it caused most failures. | 23 (10s of 11s) |
| 4:49 | 9 | Everything is in the repository and the report | Everything is in the repository and the report. Thank you for watching. | 12 (5s of 7s) |

Total narration: **616 words**, about 4.4 minutes at 140 words a minute, inside a 4:56 video.
