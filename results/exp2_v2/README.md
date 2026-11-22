# Experiment 2 (ADR-008), main result: seeds v2

**Question.** Does an *independent* reviewer (Sonnet, fresh context, adversarial prompt, sees only the issue, the diff and a checkout) catch more defects than a *non-independent* one (Haiku that also sees the author's spec, design and test report, with a neutral prompt)?

**Material.** Seven seeded PRs built from the real pipeline PRs: five with one injected defect each (S1 to S5), two real PRs unchanged as controls (C1, C2). Every defective seed passes the repo's whole test suite; the hidden tests fail on defective seeds and pass on controls (`experiment/seeded_prs/v2/*.json`). Each seed was reviewed twice per variant (14 reviews per variant). Runs: A [45007718191](https://github.com/Aasrithakalluri/tinydb/actions/runs/45007718191) and [45008349417](https://github.com/Aasrithakalluri/tinydb/actions/runs/45008349417) (S3 re-run), B [45007724687](https://github.com/Aasrithakalluri/tinydb/actions/runs/45007724687) and [45008357057](https://github.com/Aasrithakalluri/tinydb/actions/runs/45008357057). Raw reviews: `raw/`.

## Result

| | caught (verdict `changes` on defective seeds) | false approvals | false rejections (correct controls) | cost | tokens in / out |
|---|---|---|---|---|---|
| **A** Sonnet, independent | 8/10 | 2/10 | 0/4 | $0.551 | 554k / 24k |
| **B** Haiku, sees spec + design + test report | 10/10 | 0/10 | 0/4 | $0.046 | 674k / 34k |

Per seed (both runs agree in every cell): S1 nested path, S2 shared objects on cache miss, S3 skips empty documents, S5 lexical order were caught by **both**. **S4 (`multiply` silently skips a document that lacks the field) was approved by A twice and caught by B twice.**

The null/negative result for the hypothesis: independence of context did not buy detection here, and it cost 12 times as much.

## Why (from reading the reviews, not only counting)
- Every catch names the seeded defect (checked in the findings text; S3 and S5 included).
- **S4 is the whole difference.** A saw the behaviour ("a matching document with no `price` field was left unchanged, with no error") and judged it acceptable: the issue only says "same style as the other operations", and A did not compare with the sibling operations (`add`, `subtract`, `increment`), which raise `KeyError`. B caught it because **the author's spec said so** (FR-03-AC1: a missing field raises `KeyError`). B is therefore checking the diff against the *requirement*, which A never had. This is exactly what the assignment's independence rule removes, on purpose.
- So the lesson is not "shared context makes a better reviewer". It is that **a reviewer that sees only the issue cannot know unwritten conventions unless it goes looking for them** (the sibling functions are in the repository). A's prompt told it to read callers and architecture rules but not to compare the new code with its closest existing analogue.
- The pipeline rule "an approval with no executed test run is overruled" never fired: every review, in both variants, ran the suite. It is not what made the difference.
- **Neither variant escalated the contract conflict.** In S2 (derived from PR #14), which rewrites the existing contract test and the `Table.search` docstring, both variants gave `issue_type: code`; none asked for a human decision about reversing a documented design.

## What we change in the design (ADR-014)
1. We do **not** adopt variant B: the assignment requires the reviewer to see only the issue, the diff and the repository, and the S4 result shows the price of that rule rather than a reason to drop it.
2. The reviewer prompt gets an explicit step: **find the closest existing analogue of the new code and compare edge-case behaviour** (missing input, wrong type, empty input, error type). This is inside the independence rule: the analogue is part of the repository.
3. Reviewers are told to treat "removes assertions from an existing test" or "reverses a documented contract" as a finding of type `approach`. The effect of (2) and (3) is measured in the next step on **new** seeds that were not used to design the change.

## Threats to validity
1. **Tiny sample:** 7 seeds, 2 reviews each; one defect class (sibling consistency) decides the whole gap. Rates are descriptive only.
2. **Seeds are mine,** and written to be plausible small mistakes; defects were injected into real PRs but not by a real author.
3. **Variant B's artifacts match the code** only because the seeds were derived from the real PRs; in v1 they did not (confound found and removed, `results/exp2_pilot_v1/`). The defective seeds still contradict the author's spec in the same way a buggy author would.
4. **Two varying factors in B** (model and context/prompt) were changed together; this experiment cannot separate "Haiku with context" from "context" or "neutral prompt".
5. **A bug in my tooling invalidated S3 in the first dispatch** (a stale seed branch was reviewed); 2 reviews per variant (A $0.073, B $0.006) were discarded and S3 re-run after a guard was added. The invalid rows are kept in `results_*_all_including_invalid.jsonl`.
6. **The same hidden-test authors** (me) also labelled the defects.
