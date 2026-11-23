#!/usr/bin/env python3
"""Builds the silent demo video (demo.mp4) and the exact recording script from ONE source of truth: SLIDES.

  python video/build.py            -> video/slides/*.html, video/frames/*.png, demo.mp4, video/script.md, video/script.html, video/script.pdf

The video has no voice-over: the author records her own voice, following video/script.pdf (every line has the time at
which it starts, and each slide stays on screen long enough for its line at a normal speaking pace).
All facts shown come from the repository (results/, architecture/) and from the real GitHub pages of the fork.
"""
import html, json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = ROOT / "video"
CH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 1280, 720

# ------------------------------------------------------------------ real data used on the slides
def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout.strip()

design_commit = sh("git", "log", "-1", "--format=%ad", "--date=format:%H:%M", "--grep=Design first: component", "--all")
phase3_commit = sh("git", "log", "-1", "--format=%ad", "--date=format:%H:%M", "--grep=Phase 3: AutoSE orchestrator", "--all")
manifest = (ROOT / "experiment/hidden_tests/MANIFEST.sha256").read_text().splitlines()
mainfest_lines = "\n".join(f"{l.split()[0][:12]}…  {l.split()[1]}" for l in manifest)
issue1_body = (ROOT / "experiment/issues/issue-1.md").read_text()
inj = (ROOT / "experiment/security/injection-issue.md").read_text()
mm = re.search(r'<pre class="mermaid">\s*(flowchart LR.*?)</pre>', (ROOT / "report/report_v2.html").read_text(), re.S)
COMPONENT_MERMAID = mm.group(1).strip()

_a = inj.split("---")[1].strip().replace("**", "")
ATTACK = _a[:300].rsplit(" ", 1)[0] + " …"

# ------------------------------------------------------------------ shared design
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1280px;height:720px;font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;background:#f4f6fa;color:#14213d;position:relative;overflow:hidden}
.top{position:absolute;left:0;top:0;width:1280px;height:54px;background:#14213d;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 34px;font-size:19px;letter-spacing:.3px}
.top b{color:#8ecbff}.clock{font-family:Menlo,monospace;color:#cfd8e8;font-size:17px}
.main.c{display:flex;flex-direction:column;justify-content:center}.main{position:absolute;left:0;top:54px;width:1280px;height:612px;padding:26px 40px}
.foot{position:absolute;left:0;bottom:0;width:1280px;height:54px;background:#fff;border-top:1px solid #d5dbe6}
.bar{position:absolute;left:0;top:0;height:5px;background:#1f6feb}
.cap{position:absolute;left:40px;top:14px;font-size:20px;color:#14213d;font-weight:600}
h1{font-size:46px;line-height:1.1}h2{font-size:34px;margin-bottom:14px}h3{font-size:22px;margin-bottom:8px}
p,li{font-size:22px;line-height:1.35}ul{padding-left:26px}
.card{background:#fff;border:1px solid #d5dbe6;border-radius:14px;padding:18px 22px;box-shadow:0 2px 6px rgba(20,33,61,.08)}
.row{display:flex;gap:22px}.col{flex:1}
.tag{display:inline-block;background:#e8f1ff;color:#1f4fb4;border-radius:999px;padding:2px 12px;font-size:17px;margin-right:6px}
.ok{color:#1a7f37;font-weight:700}.bad{color:#cf222e;font-weight:700}.mut{color:#5b6b86}
.mono{font-family:Menlo,Consolas,monospace}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #d5dbe6;padding:6px 10px;text-align:left;font-size:17px;vertical-align:top}
th{background:#e9eef7}tr.mine td{background:#fff7e0}
.browser{border:1px solid #b9c3d6;border-radius:10px;overflow:hidden;background:#fff;box-shadow:0 4px 14px rgba(20,33,61,.18)}
.browser .u{height:30px;background:#e9edf4;border-bottom:1px solid #c9d1e0;font-size:14px;color:#52607a;display:flex;align-items:center;padding-left:14px;font-family:Menlo,monospace}
.browser .v{overflow:hidden;position:relative}.browser img{display:block;position:absolute;left:0}
.pill{display:inline-block;border-radius:999px;padding:3px 14px;font-size:18px;font-weight:700}
.big{font-size:64px;font-weight:800}.hl{background:#fff2a8;padding:0 4px}
.bar2{height:34px;border-radius:6px;margin:6px 0;color:#fff;font-weight:700;font-size:19px;display:flex;align-items:center;padding-left:12px}
"""

def shot(name, x0, y0, wpx, hpx, scale, url):
    """a cropped real screenshot inside a browser frame; (x0,y0) is the crop origin in the original image"""
    wpx = min(wpx, int((1280 - x0) * scale))
    return (f'<div class="browser" style="width:{wpx}px"><div class="u">{html.escape(url)}</div>'
            f'<div class="v" style="height:{hpx}px"><img src="../shots/{name}.png" '
            f'style="width:{int(1280*scale)}px;left:{-int(x0*scale)}px;top:{-int(y0*scale)}px"></div></div>')

def fmt(t):
    return f"{int(t)//60}:{int(t)%60:02d}"

# ------------------------------------------------------------------ the slides (scene, title, seconds, on-screen, narration)
S = []
def add(scene, stitle, dur, caption, narration, body, extra_head="", center=False):
    S.append(dict(scene=scene, stitle=stitle, dur=dur, caption=caption, narration=narration, body=body, head=extra_head, center=center))

# ---- Scene 1: hook
add(1, "The idea", 7, "One label in, one reviewed pull request out",
    "Hi, I'm Aasritha Kalluri. In this video I'll show how I built a small AI team that fixes a software bug, from start to finish.",
    """<div style="text-align:center;margin-top:70px"><div class="big" style="color:#1f6feb">AutoSE</div>
<h1 style="margin-top:14px">Label an issue.<br>Get a tested, reviewed pull request.</h1>
<p class="mut" style="margin-top:34px;font-size:26px">Aasritha Kalluri &middot; Roll no. 2025204019 &middot; Assignment 3</p>
<p class="mono mut" style="margin-top:8px;font-size:20px">github.com/Aasrithakalluri/tinydb</p></div>""")
add(1, "The idea", 9, "Five real issues, each started by one label",
    "It's called AutoSE. You add one label to a bug report, and a few minutes later a tested fix is waiting for you to review. I built it on a copy of the library tinydb.",
    '<div class="row"><div>' + shot("issues", 255, 180, 800, 470, 0.62, "github.com/Aasrithakalluri/tinydb/issues") + '</div>'
    '<div class="col"><div class="card"><h3>A maintainer adds the label <span class="tag">autose</span></h3>'
    '<p class="mut">That is the whole interface.</p></div><div class="card" style="margin-top:16px"><h3>Then agents do the work</h3>'
    '<p>spec &rarr; design &rarr; code &rarr; tests &rarr; pull request &rarr; independent review</p></div></div></div>')

# ---- Scene 2: setup
add(2, "Setup", 10, "A fork pinned to one commit, protected, with a secret key",
    "First, setup. I copied tinydb to my own account and fixed it at one exact version. The main branch is protected, and my API key is stored as a secret.",
    '<div class="row"><div>' + shot("repo", 0, 70, 760, 520, 0.594, "github.com/Aasrithakalluri/tinydb") + '</div>'
    '<div class="col"><div class="card"><h3>Pinned commit</h3><p class="mono">edff96a</p></div>'
    '<div class="card" style="margin-top:14px"><h3>Branch protection</h3><p>master changes only by pull request (a direct push was rejected)</p></div>'
    '<div class="card" style="margin-top:14px"><h3>Secrets</h3><p>API key stored as a repository secret, never in code or logs</p></div></div></div>')
add(2, "Setup", 12, "Reused my A1 skill and A2 architecture; five issues",
    "I reused my skill and architecture document from earlier assignments, and wrote five test issues: two bugs, two features, and one vague request.",
    """<div class="row"><div class="card col"><h3>Reused</h3><ul><li><b>A1</b>: requirements skill (spec with testable criteria)</li>
<li><b>A2</b>: ARCHITECTURE.md (the design stage reads it)</li></ul></div>
<div class="card col"><h3>Five issues, written like real users</h3><ul><li>2 bug reports</li><li>2 small feature requests</li><li>1 vague request</li></ul></div></div>
<div class="card" style="margin-top:20px"><h3>Issue #1 (bug), as a user wrote it</h3>
<p class="mono" style="font-size:19px">db.search(where('nickname') != 'bob')   # skips documents without the field<br>db.search(~(where('nickname') == 'bob'))  # returns them: two different answers</p></div>""", center=True)
add(2, "Setup", 8, "Hidden tests stayed private; their hashes came first",
    "I wrote hidden tests to grade fairly, kept them private, and committed their fingerprints first so I could not quietly change them. Spending was capped at five dollars.",
    f"""<div class="row"><div class="card col"><h3>Hidden acceptance tests</h3><p>Kept outside the repository while the agents ran; released only afterwards.</p>
<pre class="mono" style="font-size:17px;margin-top:10px;color:#14213d">{html.escape(mainfest_lines)}</pre></div>
<div class="card col"><h3>Validated</h3><p>Two independent fixes per issue pass them</p><h3 style="margin-top:18px">Hard spending cap</h3><p class="big" style="font-size:54px">$5</p></div></div>""", center=True)

# ---- Scene 3: design before code + architecture
add(3, "Design before code", 8, "ADRs and views were merged before any agent code",
    "Before building anything, I wrote the design. The diagrams and first decision records were merged before any helper code existed.",
    f"""<div style="margin-top:36px" class="row"><div class="card col" style="border-left:8px solid #1a7f37"><h3>{design_commit} &middot; PR #7</h3><p><b>Design first</b>: component, sequence and stage views, ADR-001 to ADR-010</p></div>
<div style="align-self:center;font-size:40px">&rarr;</div>
<div class="card col" style="border-left:8px solid #1f6feb"><h3>{phase3_commit} &middot; PR #8</h3><p><b>Then the code</b>: orchestrator, agents, checks, workflow</p></div></div>
<p class="mut" style="margin-top:34px;text-align:center">The git history shows the order.</p>""")
add(3, "Design before code", 14, "Three agents, one deterministic orchestrator, a human at the end",
    "Three AI helpers. A Planner turns the issue into a checklist. A Builder writes code and tests. A separate Reviewer checks it. A plain Python program runs the steps, and a human decides the merge.",
    '<div style="margin-top:-12px"><pre class="mermaid">' + COMPONENT_MERMAID + '</pre></div>'
    '<div class="row" style="margin-top:6px"><div class="card col" style="padding:10px 16px"><b>Agents never call each other</b><br><span class="mut" style="font-size:18px">only files are handed over</span></div>'
    '<div class="card col" style="padding:10px 16px"><b>Every pass or fail is code</b><br><span class="mut" style="font-size:18px">not an agent\'s opinion</span></div>'
    '<div class="card col" style="padding:10px 16px"><b>A human decides the merge</b><br><span class="mut" style="font-size:18px">the workflow never merges</span></div></div>',
    extra_head='<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script><script>mermaid.initialize({startOnLoad:true,theme:"neutral",flowchart:{useMaxWidth:true,htmlLabels:true,curve:"basis",subGraphTitleMargin:{top:8,bottom:46}},themeVariables:{fontSize:"15px"}});</script>')

# ---- Scene 4: one complete run (issue #1)
add(4, "One complete real run", 8, "Six stages: an artifact and a check for each",
    "A run has six steps. After each step, ordinary code, not an AI, checks the output before the next step starts.",
    """<table><tr><th>#</th><th>Stage</th><th>Agent</th><th>Artifact</th><th>Check (code decides)</th></tr>
<tr><td>1</td><td>Requirements</td><td>Planner (Haiku)</td><td class="mono">spec.md</td><td>every criterion testable</td></tr>
<tr><td>2</td><td>Design</td><td>Planner</td><td class="mono">design.md</td><td>named files and functions exist</td></tr>
<tr><td>3</td><td>Implementation</td><td>Builder (Haiku)</td><td class="mono">diff.patch</td><td>the code builds</td></tr>
<tr><td>4</td><td>Testing</td><td>Builder</td><td class="mono">test_report.md</td><td>full suite green, every criterion tested</td></tr>
<tr><td>5</td><td>Release</td><td>orchestrator (code)</td><td class="mono">pr.md</td><td>PR open, CI passes</td></tr>
<tr><td>6</td><td>Review</td><td>Reviewer (Sonnet)</td><td class="mono">review.md</td><td>approve, or 2 rounds used</td></tr></table>""")
add(4, "One complete real run", 8, "The trigger: a real bug report and one label",
    "A real example: a bug report says a not-equal search skips records that lack the field. I add the label autose.",
    f"""<div class="row"><div class="card" style="flex:1.6"><h3>Issue #1 <span class="tag">autose</span></h3>
<p><b>`!=` skips documents that don't have the field, but `~(... == ...)` doesn't</b></p>
<p class="mut" style="margin-top:10px">{html.escape(issue1_body.split(chr(10))[2])}</p>
<p style="margin-top:10px">&ldquo;Same logical question, two different answers, which cost me an afternoon.&rdquo;</p></div>
<div class="col"><div class="card" style="text-align:center"><p class="mut">label added</p><p class="big" style="font-size:42px;color:#6f42c1">autose</p></div>
<div class="card" style="margin-top:16px"><p>The workflow starts for this issue only if the person has <b>write access</b>.</p></div></div></div>""")
add(4, "One complete real run", 10, "Real log of the run: about three minutes, $0.07",
    "The Planner wrote twelve requirements. The Builder changed the code and tested each one. Then the program ran the whole test suite itself.",
    '<div class="row"><div class="card" style="flex:1.25"><h3>Orchestrator log (real)</h3><pre class="mono" style="font-size:15.5px;line-height:1.55">'
    '07:02:18  planner   spec ok: <span class="hl">12 acceptance criteria</span>\n07:02:31  planner   design ok\n'
    '07:02:45  builder   implementation builds, diff 42 lines\n07:03:10  builder   <span class="hl">all tests pass</span>, every criterion has a test\n'
    '07:04:59  release   PR #15 opened, <span class="hl">CI ok</span>\n07:05:18  reviewer  <span class="hl">approved</span>\n\n'
    '<b>3 minutes</b>  &middot;  <b>$0.070</b>  &middot;  428k tokens in, 26k out</pre></div>'
    '<div>' + shot("run", 0, 180, 460, 380, 0.36, "github.com/.../actions/runs/44996285044") + '<p class="mut" style="margin-top:8px;font-size:16px">GitHub Actions: Success, 1 artifact</p></div></div>')
add(4, "One complete real run", 8, "Every stage leaves an artifact",
    "Every step leaves a file behind: requirements, design, code change, and test report. All two hundred forty-two tests passed.",
    """<div class="row"><div class="card col"><h3 class="mono">spec.md</h3><p style="font-size:18px">FR-01-AC1: query <span class="mono">!= 'bob'</span> on a document without the field &rarr; returns True</p><p class="mut" style="font-size:16px">12 criteria, each "situation &rarr; result"</p></div>
<div class="card col"><h3 class="mono">design.md</h3><p style="font-size:18px" class="mono">tinydb/queries.py :: Query.__ne__<br>tests/test_queries.py (new)</p></div></div>
<div class="row" style="margin-top:18px"><div class="card col"><h3 class="mono">diff.patch</h3><p style="font-size:18px">2 files &middot; +86 / &minus;3</p></div>
<div class="card col"><h3 class="mono">test_report.md</h3><p style="font-size:18px"><span class="ok">242 passed</span>, run by the orchestrator itself, not reported by the agent</p></div></div>""", center=True)
add(4, "One complete real run", 10, "The pull request opens and CI passes",
    "The fix became a pull request, and the automatic checks passed. The Reviewer then looked from a clean copy, seeing only the issue and the change.",
    '<div class="row"><div>' + shot("pr15", 0, 130, 760, 540, 0.594, "github.com/Aasrithakalluri/tinydb/pull/15") + '</div>'
    '<div class="col"><div class="card"><h3>Pull request #15</h3><p>Opened by the workflow; closes issue #1; the 12 acceptance criteria are in the description</p></div>'
    '<div class="card" style="margin-top:14px"><h3>Repository CI</h3><p class="ok">green</p></div>'
    '<div class="card" style="margin-top:14px"><h3>Reviewer sees</h3><p>only the issue, the diff, and a clean checkout</p></div></div></div>')
add(4, "One complete real run", 12, "The independent review, then a person decides",
    "It ran the tests and its own examples, then approved. About three minutes and seven cents. The pull request stays open; only a person merges.",
    '<div class="row"><div>' + shot("pr15", 0, 1255, 700, 535, 0.547, "…/pull/15  (review comment, Sonnet)") + '</div>'
    '<div class="col"><div class="card"><h3>What the reviewer did</h3><ul style="font-size:19px"><li>ran the full suite: 242 passed</li><li>ran its own experiments (cached queries, hashes, nested paths)</li><li>checked the architecture constraints</li></ul></div>'
    '<div class="card" style="margin-top:14px"><p><span class="pill" style="background:#dafbe1;color:#1a7f37">verdict: approve</span></p><p style="margin-top:10px"><b>Not merged.</b> The workflow never merges; a person decides.</p></div></div></div>')

# ---- Scene 5: safety and control
add(5, "Control and safety", 22, "Hostile input, spending and loops are bounded",
    "Automation needs limits. Only people with write access can start a run, and spending and time are capped. A malicious issue told the helpers to leak secrets; they ignored it. I also forced failures to prove the retries work.",
    '<div class="row"><div class="card" style="flex:1;border-left:8px solid #cf222e"><h3 style="color:#cf222e">A real attack, written as an issue</h3>'
    f'<p class="mono" style="font-size:16px;line-height:1.45">{html.escape(ATTACK)}</p>'
    '<p style="margin-top:12px"><b class="ok">Resisted</b> at every stage; the Planner logged it as risk RSK-01; no secret in any artifact or log.</p></div>'
    '<div class="card" style="flex:1"><h3>What holds the line</h3><ul style="font-size:20px;line-height:1.6">'
    '<li>Only people with <b>write access</b> start a run</li><li>One run per issue; a second trigger <b>queues</b></li>'
    '<li>Hard caps: $0.60 per run (a $0.02 test cap stopped one)</li><li>Agents get least-privilege tools and <b>never see the token</b></li>'
    '<li>Retry, <b>redesign</b> and reviewer &ldquo;changes&rdquo; loops verified (fault-injected)</li></ul></div></div>'
    '<div class="row" style="margin-top:22px"><div class="card col"><b>Injection test</b><br><span class="ok">0 secrets</span> found in the repository, its full history and 29 workflow logs</div>'
    '<div class="card col"><b>Budget test</b><br>run stopped at <b>$0.016</b> of a $0.02 cap, with the reason written down</div>'
    '<div class="card col"><b>Back-edge run</b><br>three failures, a redesign and a reviewer &ldquo;changes&rdquo;, then DONE for <b>$0.128</b></div></div>', center=True)

# ---- Scene 6: decisions and what went wrong
ADR = [("001", "Splitting the work", "3 agents; release is code", "Accepted", 1), ("002", "Control flow", "one Python orchestrator", "Accepted", 1),
       ("003", "Hand-offs", "files, never transcripts", "Accepted", 0), ("004", "State", "artifacts + status comment", "Superseded by 011", 0),
       ("005", "Tools", "per-role allowlists, no token", "Accepted", 0), ("006", "Models", "Haiku builds, Sonnet reviews", "Accepted", 1),
       ("007", "Checks", "deterministic code decides", "Accepted", 0), ("008", "Reviewer independence", "fresh context, no push", "Accepted; Exp 2 negative", 0),
       ("009", "Safety", "hard caps, issue text is data", "Accepted", 0), ("010", "Triggers", "write access, one run per issue", "Accepted", 0),
       ("011", "State (replaces 004)", "restore code, reuse PR, rebase", "Accepted", 0), ("012", "Lint and vague issues", "tagged criteria; assume", "Accepted", 0),
       ("013", "Ask the human", "/autose ask, /autose go", "Accepted", 1), ("014", "Compare with siblings", "reviewer prompt change", "Proposed, not adopted", 0)]
rows = "".join(f'<tr class="{"mine" if m else ""}"><td>{a}</td><td>{d}</td><td>{c}</td><td>{s}</td></tr>' for a, d, c, s, m in ADR)
add(6, "Decisions and what went wrong", 12, "14 decision records; the highlighted ones are my own decisions",
    "I wrote fourteen decision records. Three were mine: three helpers, one controlling program, and a cheaper model to build with a stronger one to review.",
    f'<table style="font-size:15px"><tr><th>ADR</th><th>Decision</th><th>Chosen</th><th>Status</th></tr>{rows}</table>'
    '<p class="mut" style="margin-top:8px;font-size:16px">Highlighted: my own decisions and ideas (D1, D2, D6, the human gate). Each ADR is in first person with my reasons.</p>'.replace("font-size:15px","font-size:15px"))
add(6, "Decisions and what went wrong", 12, "11 failed attempts, none caused by the agents",
    "Eleven attempts failed along the way, none the AI's fault. They were my plumbing mistakes, including a wrong first restart design, which I replaced.",
    """<h3>Where the 11 failed attempts came from</h3><table><tr><th>Cause</th><th>Attempts</th><th>What it changed</th></tr>
<tr><td>Restart and restore logic (state without the code, a second PR, wrong artifact)</td><td>4</td><td><b>ADR-004 superseded by ADR-011</b></td></tr>
<tr><td>CI around the restart (tests collected, old base commit)</td><td>2</td><td>ADR-011 addendum</td></tr>
<tr><td>My own checks (a lint that rejected a good spec; a vague issue)</td><td>2</td><td>ADR-012, ADR-013</td></tr>
<tr><td>Setup (invalid workflow file, a repository setting)</td><td>2</td><td>fixed</td></tr>
<tr><td>A budget cap set to $0.02 on purpose</td><td>1</td><td>a test</td></tr></table>
<p class="mut" style="margin-top:12px">A reasoned decision was wrong; one real run proved it. The old ADR stays, marked Superseded.</p>""", center=True)
add(6, "Decisions and what went wrong", 10, "The vague issue: the pipeline asks the human",
    "For the vague issue, the system no longer guesses. It stops, asks me questions, and continues only after I answer.",
    """<div class="row"><div class="card" style="flex:1.2"><h3>Issue #5: &ldquo;Results come back in a strange order&rdquo;</h3>
<p style="font-size:19px">The run <b>pauses</b> and posts questions:</p><ul style="font-size:19px"><li>1. Which order: ascending id, or insertion order?</li><li>2. Should an updated document keep its position?</li><li>3. Must it hold for custom storages?</li></ul></div>
<div class="card col"><h3>I give the green flag</h3><p class="mono" style="font-size:20px">/autose go 1a, 2a, 3a</p><p class="mut" style="margin-top:12px">The run resumes and finishes. Costs nothing while it waits.</p></div></div>""", center=True)

# ---- Scene 7: experiments
def bars(title, items, unit="", note=""):
    out = f'<h3 style="font-size:26px">{title}</h3>'
    for label, val, mx, color, txt in items:
        pct = max(4, int(val / mx * 100))
        inside = pct >= 30
        out += (f'<div class="mut" style="font-size:20px;margin-top:14px">{label}</div>'
                f'<div style="display:flex;align-items:center"><div class="bar2" style="width:{pct}%;height:46px;background:{color};font-size:24px;margin:6px 0">{txt if inside else ""}</div>'
                f'{"" if inside else f"<span style=\"font-size:24px;font-weight:700;margin-left:12px;color:{color}\">{txt}</span>"}</div>')
    return out + (f'<p class="mut" style="margin-top:10px;font-size:17px">{note}</p>' if note else "")
add(7, "Experiments", 16, "One agent vs three: same quality, 70% more cost",
    "Experiment one: do three helpers beat one? Quality was similar, ten of ten against nine of ten, but splitting cost seventy percent more. It also exposed a bug I then fixed.",
    '<div class="row"><div class="card col">' + bars("Cost per run", [("3 agents", 0.0202, 0.0202, "#1f6feb", "$0.0202"), ("1 agent", 0.0118, 0.0202, "#6f42c1", "$0.0118")]) + '</div>'
    '<div class="card col">' + bars("Hidden tests passed (runs of 10)", [("3 agents", 10, 10, "#1f6feb", "10 / 10"), ("1 agent", 9, 10, "#6f42c1", "9 / 10")]) + '</div></div>'
    '<div class="card" style="margin-top:18px"><b>ADR-001 tested</b>, 20 runs. The one miss: the single agent saw a conflict with a documented contract and did not change the code, but the run was still reported <b>DONE</b>. A gap in my checks.</div>', center=True)
add(7, "Experiments", 18, "Independent reviewer: no better at catching defects",
    "Experiment two: does an independent reviewer catch more? On planted bugs, no: eight of ten, against ten of ten for a reviewer that also read the requirements.",
    '<div class="row"><div class="card col">' + bars("Seeded defects caught (of 10 reviews)", [("Independent Sonnet reviewer", 8, 10, "#1f6feb", "8 / 10"), ("Haiku that also sees the spec", 10, 10, "#6f42c1", "10 / 10")]) + '</div>'
    '<div class="card col">' + bars("Cost of the 14 reviews", [("Independent Sonnet", 0.551, 0.551, "#1f6feb", "$0.551"), ("Haiku with spec", 0.046, 0.551, "#6f42c1", "$0.046")]) + '</div></div>'
    '<div class="card" style="margin-top:18px"><b>ADR-008 tested</b> on 7 seeded PRs (real fixes with one injected defect, suite still green). It missed <i>multiply silently skips a missing field</i>: the issue never said what should happen. <b>Independence stays as a rule, not a proven benefit.</b></div>', center=True)
add(7, "Experiments", 12, "A fix was tested against a criterion set in advance",
    "I tried a fix, judged by a rule set beforehand. It wrongly rejected a correct change, so I did not adopt it.",
    """<div class="card"><h3>ADR-014: compare new code with its closest analogue</h3><table><tr><th>Pre-registered criterion</th><th>Result</th></tr>
<tr><td>Catch the three seeded defects in every review</td><td class="ok">met</td></tr>
<tr><td>Label a reversal of documented behaviour as an <span class="mono">approach</span> problem</td><td class="ok">met</td></tr>
<tr><td>Approve every correct control</td><td class="bad">not met: a correct change rejected twice</td></tr></table>
<p style="margin-top:14px"><b>Status: Proposed, not adopted.</b> I did not tune it afterwards to pass.</p></div>""", center=True)

# ---- Scene 8: results and honesty
add(8, "Results and honesty", 14, "All five issues reached a reviewed pull request",
    "All five issues reached a reviewed pull request for six to nine cents each. Hidden tests pass, except the vague issue missed one extra reading.",
    """<div class="row"><div class="col"><h3>First-try pass, final run of each issue</h3><table><tr><th>Stage</th><th>Pass</th></tr>
<tr><td>Requirements</td><td>5/5</td></tr><tr><td>Design</td><td>4/5</td></tr><tr><td>Implementation</td><td>5/5</td></tr><tr><td>Testing</td><td>5/5</td></tr><tr><td>Release (CI)</td><td>5/5</td></tr><tr><td>Review approved</td><td>5/5</td></tr></table></div>
<div class="col"><h3>Hidden tests and cost</h3><table><tr><th>Issue</th><th>Tests</th><th>Cost</th></tr>
<tr><td>#3 count()</td><td>3/3</td><td>$0.058</td></tr><tr><td>#1 !=</td><td>3/3</td><td>$0.070</td></tr><tr><td>#2 mutation</td><td>3/3</td><td>$0.086</td></tr>
<tr><td>#4 multiply</td><td>4/4</td><td>$0.084</td></tr><tr><td>#5 vague</td><td>5/6</td><td>$0.092</td></tr></table></div></div>""", center=True)
add(8, "Results and honesty", 14, "Limits and AI use, stated plainly",
    "Honest limits: small samples, costs are my estimates, and I wrote both issues and tests. An AI assistant wrote most code; the decisions and reasons are mine.",
    """<div class="row"><div class="card col"><h3>Limits</h3><ul style="font-size:20px"><li>Small samples: 5 issues, 10 runs per variant</li><li>Issues, hidden tests and seeded defects written by me</li><li>Cost about $3.4 is my own estimate, not the console's</li><li>My own bugs are logged, not hidden</li></ul></div>
<div class="card col"><h3>AI use, disclosed</h3><ul style="font-size:20px"><li>Claude Code wrote the code and drafted the text</li><li>The decisions and their reasons are mine</li><li>All 14 ADRs read and adopted by me</li><li>Every run, PR and result is real and linked</li></ul></div></div>""", center=True)

# ---- Scene 9: close
add(9, "Hindsight and close", 8, "What I would change first",
    "If I started again, I would fix saving and restarting progress first, and test it before spending money, since it caused most failures.",
    """<div class="card" style="margin-top:30px;border-left:8px solid #1f6feb"><h3>Hindsight</h3><p style="font-size:26px">I would change <b>state and restart</b> first, and test it on a stub run before any paid agent run: it caused most of the failures.</p>
<p class="mut" style="margin-top:14px">Keep: the deterministic orchestrator, the deterministic checks, and the independent reviewer as a rule.</p></div>""", center=True)
add(9, "Hindsight and close", 8, "Everything is in the repository and the report",
    "Everything is in the repository and the report. Thank you for watching.",
    """<div style="text-align:center;margin-top:70px"><div class="big" style="color:#1f6feb">Thank you</div>
<p style="margin-top:26px;font-size:28px"><b>github.com/Aasrithakalluri/tinydb</b></p>
<p class="mut" style="margin-top:10px;font-size:22px">architecture/ &middot; workflow/ &middot; experiment/ &middot; results/ &middot; report</p>
<p class="mut" style="margin-top:22px;font-size:22px">Aasritha Kalluri &middot; 2025204019</p></div>""")

import math
for s_ in S:      # every slide stays up for its line at a calm 140 words a minute, plus 1.5 s; never much shorter than first designed
    s_["dur"] = max(math.ceil(len(s_["narration"].split()) / 140 * 60 + 1.0), round(s_["dur"] * 0.6))
TOTAL = sum(s["dur"] for s in S)
assert TOTAL <= 296, f"video would be {TOTAL}s"

def page(i, s, t0):
    bar = f'<div class="bar" style="width:{t0/TOTAL*100:.1f}%"></div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style>{s["head"]}</head><body>'
            f'<div class="top"><span>Scene {s["scene"]} &middot; <b>{html.escape(s["stitle"])}</b></span><span class="clock">{fmt(t0)}</span></div>'
            f'<div class="main{" c" if s["center"] else ""}">{s["body"]}</div><div class="foot">{bar}<div class="cap">{html.escape(s["caption"])}</div></div></body></html>')

def build_frames():
    for d in ("slides", "frames", "segs"):
        shutil.rmtree(V / d, ignore_errors=True); (V / d).mkdir(parents=True)
    t = 0
    for i, s in enumerate(S, 1):
        p = V / "slides" / f"{i:02d}.html"; p.write_text(page(i, s, t)); s["t0"] = t; t += s["dur"]
        out = V / "frames" / f"{i:02d}.png"
        budget = "20000" if s["head"] else "4000"
        subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}", f"--virtual-time-budget={budget}",
                        f"--screenshot={out}", f"file://{p}"], capture_output=True)
        if not out.exists(): sys.exit(f"frame {i} failed")
        print(f"frame {i:02d}  scene {s['scene']}  {fmt(s['t0'])}  {s['dur']:>2}s  {s['caption'][:58]}", flush=True)

def build_video():
    lst = []
    for i, s in enumerate(S, 1):
        d = s["dur"]; seg = V / "segs" / f"{i:02d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(d), "-i", str(V / "frames" / f"{i:02d}.png"),
                        "-f", "lavfi", "-t", str(d), "-i", "anullsrc=r=44100:cl=stereo",
                        "-vf", f"scale={W}:{H},format=yuv420p,fade=t=in:st=0:d=0.25,fade=t=out:st={d-0.25}:d=0.25", "-r", "25",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-shortest", str(seg)], check=True)
        lst.append(f"file '{seg}'")
    (V / "segs" / "list.txt").write_text("\n".join(lst))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(V / "segs" / "list.txt"), "-c", "copy", str(ROOT / "demo.mp4")], check=True)

def write_script():
    words = lambda t: len(t.split())
    rows = []; md = ["# Demo video: exact recording script\n",
        f"Total video length **{fmt(TOTAL)}** (limit 5:00). The video is silent: read each line aloud **when its time appears** in the corner of the screen. "
        "Calm speaking pace (about 140 words a minute) fits every slide with a second or two to spare. Stay a little under the pace, pause at full stops, and do not rush.\n",
        "| Time | Scene | On screen | Say (exact words) | Words |\n|---|---|---|---|---|"]
    cards = []
    cur = None
    for s in S:
        w = words(s["narration"]); need = w / 140 * 60
        md.append(f"| {fmt(s['t0'])} | {s['scene']} | {s['caption']} | {s['narration']} | {w} ({need:.0f}s of {s['dur']}s) |")
        if s["scene"] != cur:
            cards.append(f'<h2>Scene {s["scene"]}: {html.escape(s["stitle"])}</h2>'); cur = s["scene"]
        cards.append(f'<div class="line"><span class="t">{fmt(s["t0"])}</span><span class="say">{html.escape(s["narration"])}</span>'
                     f'<span class="on">on screen: {html.escape(s["caption"])} &middot; {s["dur"]}s</span></div>')
        rows.append((s["t0"], w, s["dur"]))
    allw = sum(r[1] for r in rows)
    md.append(f"\nTotal narration: **{allw} words**, about {allw/140:.1f} minutes at 140 words a minute, inside a {fmt(TOTAL)} video.\n")
    (V / "script.md").write_text("\n".join(md))
    (V / "script.html").write_text("""<!doctype html><html><head><meta charset="utf-8"><title>Recording script</title><style>
@page{size:A4;margin:14mm}body{font-family:"Helvetica Neue",Arial,sans-serif;color:#14213d;font-size:13pt;line-height:1.45}
h1{font-size:21pt}h2{font-size:14.5pt;margin:12pt 0 4pt;border-bottom:1pt solid #8a97b1;padding-bottom:2pt}
.intro{font-size:11pt;color:#34425e;margin-bottom:6pt}.line{margin:6pt 0;page-break-inside:avoid}
.t{display:inline-block;width:44pt;font-family:Menlo,monospace;font-weight:700;color:#1f4fb4;vertical-align:top}
.say{display:inline-block;width:405pt;font-size:14pt;font-weight:600}.on{display:block;margin-left:44pt;font-size:9.5pt;color:#6a7790}
</style></head><body><h1>Demo video: recording script</h1><p class="intro">Silent video, """ + fmt(TOTAL) + """ long (limit 5:00). Read each line aloud when its time shows in the top-right corner of the screen.
Speak at a calm pace (about 140 words a minute); every slide leaves at least a second and a half to spare. Record the voice in one take per scene, then add it to demo.mp4 in any video editor.</p>"""
        + "".join(cards) + "</body></html>")
    subprocess.run([CH, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={V/'script.pdf'}", f"file://{V/'script.html'}"], capture_output=True)

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("all", "frames"): build_frames()
    if step in ("all", "video"): build_video()
    if step in ("all", "script"):
        if step == "script":
            t = 0
            for s in S: s["t0"] = t; t += s["dur"]
        write_script()
    print("done; total", fmt(TOTAL))
