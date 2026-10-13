# TENANTPROOF agent operating policy

Scope: **synthetic demo** only. Read `contracts/tenant-boundaries.yaml`.

- Authorized writes: `app/` and `tests/isolation/` only, except explicit human-approved initial bootstrap changes.
- Never remove or weaken isolation controls, fake test output, or alter `.gitlab-ci.yml`, `.gitlab/duo/`, `deploy/`, GitLab branch protection, secrets, or policies.
- Do not use user-controlled tenant headers as authority. Validate JWT subject and issuer/audience.
- Reproduce a suspected vulnerability with a red test; preserve authorized access with green tests.
- Never use real data. Do not commit tokens, URLs with credentials or cloud keys.
- CI is the gate. A Duo statement is not a release approval.
- If you cannot push a patch or execute tests, report `INCONCLUSIVE`; do not imply full autonomy.
