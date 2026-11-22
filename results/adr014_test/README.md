# ADR-014 test: reviewer prompt v2 (A2) against the pre-registered criterion

Pre-registration: `experiment/seeded_prs/v3/PREREGISTRATION.md` (committed before any run). Runs: A2 on S6, S7, C3 [45009457003](https://github.com/Aasrithakalluri/tinydb/actions/runs/45009457003); A2 on S4, C1, C2 [45009464209](https://github.com/Aasrithakalluri/tinydb/actions/runs/45009464209); old prompt A on S6, S7, C3 [45009471822](https://github.com/Aasrithakalluri/tinydb/actions/runs/45009471822). Two reviews per seed, 18 reviews, $0.733. Raw reviews: `raw/`.

## Criterion and outcome
| # | Criterion | Outcome |
|---|---|---|
| 1 | A2 returns `changes` on S4, S6, S7 in both runs | **Met** (6/6) |
| 2 | S7 is identified as a reversal of documented behaviour (`issue_type: approach` or an explicit finding) | **Met** (`approach` in both runs; the findings cite the docstring and the tests) |
| 3 | A2 approves C1, C2, C3 in both runs | **Not met**: C1 and C3 approved 4/4, **C2 rejected 2/2** (`approach`) |
| – | Counterfactual: old prompt A on S6, S7, C3 | caught S6 2/2 and S7 2/2 (`code`), approved C3 2/2 |

**Decision by the rule fixed in advance:** a false rejection is reported as a cost of the change and the ADR **stays Proposed**. The production prompt is **not** switched.

## What the numbers do and do not show
- **A2 fixes the S4 miss** (A missed it 2/2 in Experiment 2; A2 caught it 2/2 with the right reason: "the sibling operations raise KeyError"). S4 is the seed the change was designed on, so this alone is not evidence of generalisation.
- **On the new seeds the old prompt already worked.** A caught S6 (it read ARCHITECTURE.md constraint 5, "a query's hash must identify exactly what it matches", which the production prompt already requires) and S7 (it noticed the documented rule being reversed). So S6 and S7 **do not discriminate** between the two prompts at the verdict level (ceiling effect). The only measurable difference on them is the routing label: for S7, A2 says `approach` 2/2 and A says `code` 2/2. In the orchestrator `approach` sends the work back to the *design* stage, which is the right place for "a documented rule may not change without a decision".
- **The cost of A2 is a false rejection.** On C2 (the real PR #17, unchanged) A2 objected that `multiply` adds strict type validation "that none of the siblings do". That follows from step 6 of the prompt, and it is defensible: the issue says "same style as the other operations". C2 was labelled correct because it passes the hidden tests (4/4) and the pipeline's spec asked for validation, but the reviewer never sees that spec. So the C2 label is arguable; by the pre-registered rule it still counts as a false rejection.
- **Tokens/cost:** A2 $0.0417 per review vs A $0.0387 (+8%), more turns.

## Conclusion
Partially supported. Step 7 (documented/tested behaviour reversed without being asked → `approach`) changes routing as intended. Step 6 (compare with the closest analogue) fixes S4 but also over-fires on a deliberate, spec-backed difference. The two steps were tested together, so this experiment cannot say which one caused which effect. A cleaner follow-up would split them and use fresh seeds; tuning step 6 now to stop the C2 rejection would be fitting the prompt to a test case, so it is **not** done. ADR-014 is updated accordingly.

## Threats to validity
Two reviews per seed; seeds and prompt written by the same person in the same session (declared in advance); the S6/S7 ceiling means the generalisation question is largely unanswered; one control (C2) decides the outcome of criterion 3 and its label is debatable; steps 6 and 7 are confounded.
