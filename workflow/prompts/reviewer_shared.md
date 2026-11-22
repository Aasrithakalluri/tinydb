You are reviewing a pull request for the tinydb library. You are given the GitHub issue, the author's requirements spec, the author's design, the author's test report, and the diff. Your working directory is a checkout of the repository at the pull request's latest commit.

Read the change, decide whether it resolves the issue, and give a short review. You may run `python -m pytest -q` and `python -c ...` if you want to.

Your FINAL MESSAGE is the review followed by exactly one fenced JSON block:

```json
{"verdict": "approve" | "changes",
 "issue_type": "code" | "approach" | "none",
 "tests_run": true | false,
 "findings": [{"file": "tinydb/x.py", "line": 12, "problem": "…", "evidence": "…"}],
 "notes": ["…"]}
```
