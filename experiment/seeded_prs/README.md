# Seeded reviewer-check PRs

Real fixes with **one deliberately injected defect each** (S1 to S5), plus two correct controls (C1, C2), so the reviewer can be scored on what it catches, what it misses (false approvals) and whether it rejects correct work (false rejections).

Built and verified by `build.py`: for every seed the repo suite **passes** (so the defect is not visible from a red test run), the issue's hidden tests **fail** on defective seeds and **pass** on controls. Branches `seeded/s1` … `seeded/c2` exist in the fork; the diff against the baseline is `<ID>.patch` and the label is `<ID>.json`.

| ID | Issue | Defect (label) | Suite | Hidden tests | How a careful reviewer finds it |
|----|-------|----------------|-------|--------------|---------------------------------|
| S1 | #1 `!=` | `nested-path-missing`: fixed for top-level fields only | 230 pass | 1 of 3 fail | try a nested path; compare `q != v` with `~(q == v)` |
| S2 | #2 mutation | `copy-on-hit-only` **and** the existing contract test is rewritten, docstring left stale | 229 pass | 2 of 3 fail | mutate the *first* result; read the diff of existing tests |
| S3 | #3 `count()` | `counts-all-tables` | 229 pass | 1 of 3 fail | add a second named table |
| S4 | #4 `multiply` | `silently-skips-missing-field` (siblings raise KeyError) | 230 pass | 1 of 4 fail | compare with `add` on a document missing the field |
| S5 | #5 order | `lexical-order`: id 10 sorts before id 2 | 229 pass | 5 of 6 fail | insert 12 documents |
| C1 | #3 | none (correct) | 230 pass | 3 of 3 pass | – |
| C2 | #4 | none (correct) | 230 pass | 4 of 4 pass | – |

Expected verdict: `changes` for S1 to S5, `approve` for C1 and C2.

**Limits.** Defects were written by me, so they reflect my idea of a realistic mistake (incomplete fix, wrong scope, sibling inconsistency, wrong sort, weakened test). They are small and the diffs are short, which favours the reviewer. Seven seeds give coarse rates.
