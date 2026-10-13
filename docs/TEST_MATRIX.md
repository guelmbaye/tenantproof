# Evidence and validation matrix

| ID | Condition | Expected | Current |
|---|---|---|---|
| T01 | Tenant A reads A | HTTP 200 | Implemented local test |
| T02 | Tenant A reads B on clean source | HTTP 403 | Implemented local test |
| T03 | Tenant B reads A on clean source | HTTP 403 | Implemented local test |
| T04 | Missing auth | HTTP 401 | Implemented local test |
| T05 | M01 in temp source, conventional tests | Green | Reproduction script |
| T06 | M01 in temp source, isolation test | Red | Reproduction script |
| T07 | Duo generates contextual test | Red against M01 | Not verified |
| T08 | Duo patches M01 | Green on patched SHA | Not verified |
| T09 | Autonomous merge | No human approval | Not implemented |
| T10 | Runtime Cloud Run probe | A 200 / B 403 | Not verified |
| T11 | Safe refactor | No false positive | Not implemented |
| T12 | Separate cache leak mutation | Distinct diagnostic/repair | Not implemented |

Do not present 'expected' outcomes as observations before executing the corresponding commands and inspecting logs.
