# Hidden acceptance tests

The hidden tests are in this folder **now**, copied after the last agent run on issues 1 to 5 (Experiment 1, run 45018696619; the later back-edge run used the throwaway issue #30). Until then they were kept outside the repository on purpose. The Builder and Reviewer agents work on a checkout of this repository, so committing the tests would let them read the answers. They are kept outside the repository (`~/a3_private/hidden_tests/`) while runs are being scored, and are copied here when the last run has been scored.

To show that the tests were fixed *before* the runs they score, `MANIFEST.sha256` holds their SHA-256 hashes, committed with the pipeline's first runs. When the files are copied in, `shasum -a 256 -c MANIFEST.sha256` must pass for every file that was not deliberately changed. Any change is listed below with its reason and date.

## Change log of the hidden tests
| Date | File | Change | Reason |
|------|------|--------|--------|
| 2026-11-22 | all five | created | initial version, verified to fail on the baseline commit |
| 2026-11-22 | test_issue5_hidden.py | renamed the update-return-order test to `test_extra_...`; added 3 tests for the maintainer's answers (1a ascending id, 2a updated document keeps its position, 3a built-in storages) | written **before** the ask-mode run was resumed and before its PR was looked at; baseline fails 4/6, saved auto-mode PR passes 5/6 |

## Issue #5 scoring rule
Pass = the tests that follow from the answers (all but the one named `test_extra_*`). The `extra` test is a further reading ("`update()` returns ids ascending") that no question asked about; it is reported separately.

## Who answered the pipeline's questions on issue #5
The maintainer delegated the answers to the assistant ("do whatever you feel is most relevant, efficient, and of less cost"). The assistant answered `1a, 2a, 3a` from the issue text. This is **not** an independent human answer and is listed as a limitation in the report: the ask-mode result shows that the pipeline can use answers, not that the answers were the maintainer's own.

## Released
Copied on 2026-11-22; `shasum -a 256 -c MANIFEST.sha256` passes for all five files. Agent runs started after this date would see these files in the checkout, so none should be made on issues 1 to 5 without moving them out again.
