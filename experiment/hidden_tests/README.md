# Hidden acceptance tests

The hidden tests are **not** in this folder yet, on purpose. The Builder and Reviewer agents work on a checkout of this repository, so committing the tests would let them read the answers. They are kept outside the repository (`~/a3_private/hidden_tests/`) while runs are being scored, and are copied here when the last run has been scored.

To show that the tests were fixed *before* the runs they score, `MANIFEST.sha256` holds their SHA-256 hashes, committed with the pipeline's first runs. When the files are copied in, `shasum -a 256 -c MANIFEST.sha256` must pass for every file that was not deliberately changed. Any change is listed below with its reason and date.

## Change log of the hidden tests
| Date | File | Change | Reason |
|------|------|--------|--------|
| 2026-11-22 | all five | created | initial version, verified to fail on the baseline commit |
