# Pre-registration: testing ADR-014 (written and committed BEFORE any review of S6, S7, C3 was run)

**Hypothesis.** The reviewer prompt of ADR-014 (`workflow/prompts/reviewer_v2.md`, variant **A2**: compare new code with its closest analogue; treat reversal of documented/tested behaviour as an `approach` finding) fixes the miss seen in Experiment 2 (S4) **without** a design that was tuned on S4 alone.

**Material.** S4 (the miss; used to design the change, so it cannot prove generalisation), and three seeds that were built after the miss and are not used to write the prompt text: **S6** (hash tag copied from a sibling operator, a different sibling-convention defect in a different file), **S7** (an unrequested reversal of the documented rule that `remove(doc_ids=...)` silently skips missing ids, with the three tests that pin it rewritten), **C3** (correct control). Also the existing controls C1 and C2. Each reviewed **2 times**. Baseline: the current prompt (variant **A**) on S6, S7, C3, 2 times each.

**Success criterion for ADR-014 (all must hold):**
1. A2 returns `changes` on S4, S6 and S7 in **both** runs of each (6/6).
2. For S7, `issue_type` is `approach` **or** a finding states that existing tests/documented behaviour were reversed (both runs).
3. A2 returns `approve` on C1, C2 and C3 in both runs (no false rejection).
4. The independent prompt A is reported on S6, S7, C3 for comparison, whatever it does.

**Decision rule.** All of 1 to 3 hold → ADR-014 becomes *Accepted* and the production reviewer prompt is switched to v2. S4 caught but S6 or S7 missed → the change is overfitted to S4: ADR-014 is *Superseded* and the production prompt stays. Any false rejection → reported as a cost of the change; the ADR stays *Proposed*.

**Things that bias this test in favour of the change (declared in advance).** The seeds and the prompt were written by the same person in the same session, and the seeds exercise the two classes the prompt names. A baseline run of the old prompt on the same seeds is the only counterfactual. Two reviews per seed give coarse rates. The seeds are small, which favours any reviewer.

## Outcome (added after the runs; the text above was not changed)
Criteria 1 and 2 met; criterion 3 not met (C2 rejected 2/2). By the decision rule the ADR stays **Proposed** and the production prompt is unchanged. Details and caveats: `results/adr014_test/README.md`.
