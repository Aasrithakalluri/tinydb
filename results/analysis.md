# Results analysis (Phase 5)

All numbers come from files in this repository (`results.csv`, `runs.md`, `exp2_v2/`, `adr014_test/`, `variant_runs/`). Hidden-test scores are from running the private tests (`experiment/hidden_tests/MANIFEST.sha256` fixes their hashes) against each PR branch.

## 1. Pass rate per stage
See `stage_pass_rates.md`. Final runs of the five experiment issues: spec lint 5/5, design lint 4/5 (one retry fixed it), build 5/5, tests 5/5, release/CI 5/5, review approved in round 1 5/5. Across all attempts, **11 runs failed and none because of the agents' capability** (10 pipeline/setup defects of mine, 1 deliberate budget test).

## 2. Hidden tests per issue
| Issue | PR | Hidden tests | Remark |
|---|---|---|---|
| #3 `count()` | #10 | 3/3 | |
| #1 `!=` | #15 | 3/3 | |
| #2 mutation | #14 | 3/3 | **also rewrote the existing contract test** (`test_query_cache_documents_are_shared_with_cache`) and the docstring; any valid fix must (`experiment/validation/README.md`) |
| #4 `multiply` | #17 | 4/4 | |
| #5 vague, auto (assumed "ascending id") | #18 (closed) | 5/6 | fails only the `extra` test |
| #5 vague, ask (answers `1a, 2a, 3a`) | #26 | 5/6 | same; the answers were chosen by the assistant, not independently by the maintainer |

The hidden tests were validated with two independent fixes per issue (`experiment/validation/`): for #1, #3, #4, #5 both pass; #2 conflicts with an existing test by nature.

## 3. What the reviewer caught and where it was wrong
**On the real PRs (Sonnet, independent):** it approved all 7 PRs in round 1, always after running the suite and its own experiments, and it checked the architecture constraints each time. It never asked for changes on a real PR, so these runs give **no evidence that it catches anything**; the evidence is the seeded PRs.

**On seeded PRs with one injected defect** (`results/exp2_v2/`, `results/adr014_test/`, 2 reviews per seed):
| Seed (defect) | Production reviewer (A) | A2 (ADR-014 prompt) | Haiku + author's artifacts (B) |
|---|---|---|---|
| S1 `!=` nested path missing | caught 2/2 | – | caught 2/2 |
| S2 cache shares objects on miss | caught 2/2 | – | caught 2/2 |
| S3 `count()` skips empty documents | caught 2/2 | – | caught 2/2 |
| **S4 `multiply` silently skips missing field** | **missed 0/2** | **caught 2/2** | caught 2/2 |
| S5 lexical order | caught 2/2 | – | caught 2/2 |
| S6 hash tag copied from sibling | caught 2/2 | caught 2/2 | – |
| S7 unrequested contract reversal | caught 2/2 (`code`) | caught 2/2 (`approach`) | – |
| Controls C1, C2, C3 | approved 6/6 | C2 rejected 2/2, C1 and C3 approved 4/4 | approved 4/4 |

**Where the reviewer was wrong or weak:**
1. **S4 (A):** it saw "no error" for a missing field and accepted it, because the issue is silent and it did not compare with the sibling operations that raise `KeyError`.
2. **Contract reversals (A and B) were not escalated:** on S2 both flagged the stale docstring and the rewritten test as `code` issues; neither said "a human must decide whether a documented rule may change" (A2's step 7 does).
3. **A2 over-fired on a control:** it rejected the unchanged real PR #17 for stricter validation than its siblings (arguable, but a false rejection by the pre-registered rule).
4. **Real PR #14 (approved):** the reviewer approved a PR that inverts an existing contract test; the issue did ask for the new behaviour, so this is a judgement call, not a clear error.
5. The "approval without a test run is overruled" rule never fired: every review ran the suite.

## 4. Side-by-side comparison of the tested decisions
| Decision tested | Variants | Result | What changed in the design |
|---|---|---|---|
| **ADR-008 reviewer independence** (Exp 2, 14 reviews each) | A independent Sonnet vs B Haiku with spec, design and test report | A caught 8/10, 0/4 false rejections, $0.551; B caught 10/10, 0/4 false rejections, $0.046. **Hypothesis not supported.** The gap is one defect class where the issue is silent but the author's spec is explicit. | Independence kept (assignment rule); ADR-014 proposed |
| **ADR-014 reviewer prompt** (pre-registered) | A vs A2 | A2 fixes S4 and labels S7 `approach`; false-rejects C2 2/2; old prompt already caught S6 and S7 | Stays Proposed; production prompt unchanged |
| **ADR-013 ask vs assume** (issue #5 only) | auto vs ask | both 5/6 on hidden tests; $0.163 vs $0.092 | ask-mode kept as an option (`/autose ask`) |
| **ADR-001 one agent vs three** (Exp 1) | single vs 3-agent for stages 1 to 4 | *not run yet* | – |

Negative or null results: Exp 2 (independence did not help detection), ADR-013 (no gain in correctness), ADR-014 (a cost for the gain). They are reported as measured.
