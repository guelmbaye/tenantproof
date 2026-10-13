# TENANTPROOF — GitLab Transcend 2026

**From Green Pipeline to Proven Tenant Isolation.**

This repository is a **technical bootstrap**, not evidence of a successful GitLab Duo run or autonomous production deployment. All data are synthetic. The initial locally executable vertical slice demonstrates that conventional tests can pass even when an authorization mutation introduces a real leak, while independent boundary tests detect it.

## What works now

- FastAPI / SQLAlchemy minimal two-tenant invoice API.
- Real HS256 JWT verification with required claims and user/tenant identity matching.
- PostgreSQL option (`docker compose`); in-memory SQLite for unit tests.
- Deterministic NORTHSTAR / BLUEHARBOR fixtures.
- A genuine source mutation M01 created only inside a temporary directory.
- Conventional tests and security-boundary tests.
- GitLab CI jobs that fail when the boundary tests fail.
- Initial Duo Custom Flow YAML and GitLab Duo execution configuration.

## Prerequisites

Python 3.12, pip. Optional Docker + Compose for PostgreSQL and API service.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests
python scripts/replay_m01.py
```

Expected replay: **baseline tests green, isolation suite red** against the *temporary vulnerable copy*. The script must not be interpreted as a Duo run. A clean repository must always pass the full test suite.

For a persistent local API and PostgreSQL:

```sh
docker compose up --build -d
curl http://localhost:8080/health
docker compose down --volumes
```

`docker-compose.yml` uses local-only development credentials, binds the API to loopback and should **never** be used for a public deployment.

## Demo access

No user credentials are returned by the API. For local fixture testing, use `app.token.make_token` with the local Compose `JWT_SECRET` and synthetic user IDs in `app/fixtures.py`. Do not expose the JWT signing secret or tokens on public websites.

## GitLab Duo setup (external validation required)

1. Complete the hackathon contributor onboarding and obtain project access.
2. Commit to the new MIT-licensed project in the hackathon GitLab group.
3. Push `.gitlab/duo/agent-config.yml` to the **default** branch (GitLab reads this file from the default branch only).
4. In **AI > Flows > New flow**, use `.gitlab/duo/flows/tenantproof.yaml` as the configuration and name it **Tenant Isolation Guardian**. The local YAML file does not automatically create an AI Catalog flow.
5. Enable it and configure an **Assign reviewer** trigger; the flow expects `context:goal` to contain the MR IID. MR-created triggers use a different payload and need an adapter before use.
6. Create an MR with a controlled security regression. Assign the flow's service account as reviewer.
7. Verify the actual Duo session, its tool calls, pushed patch, CI checks, and final status. Record real URLs in `evidence/`.
8. Do **not** claim Hands-off until autonomous merge, deployment and post-deployment tests are actually verified.

The flow intentionally **does not** have a human approval component. However absence of that component does not prove the instance grants permissions to push/merge. Triggers may require Premium/Ultimate entitlement; validate in the hackathon-provided project.

## CI / deployment status

`.gitlab-ci.yml` includes a mandatory test gate and an optional Cloud Run deployment job gated by `DEPLOY_ENABLED=true`. It is **not enabled or validated**. The cloud path requires Google Workload Identity Federation, Artifact Registry, Cloud Build, Cloud SQL connectivity, a production database secret and CI-only synthetic credentials. A successful registry push is NOT equivalent to a successful Cloud Run deploy.

The Cloud Run sample is an integration scaffold; configure the Cloud SQL connection and JWT secret before enabling. Ensure GitLab branch protections and required pipeline-success settings are enabled via GitLab UI. Make all relevant jobs mandatory and avoid protected-gate changes from automated patch flows.

## Claims register

| Claim | Status |
|---|---|
| Green baseline vs red isolation after real mutation | Local test script included; independently verify by running |
| Working GitLab Duo Custom Flow | NOT YET VERIFIED |
| Duo-generated tests and patch | NOT YET VERIFIED |
| Autonomous merge (Hands-off) | NOT YET VERIFIED |
| Cloud Run deployed behavior proof | NOT YET VERIFIED |

## Safety

Do not run vulnerable code on a public endpoint. This repository only operates on synthetic invoice data. CI reports, not LLM assertions, determine release readiness. Review prompt-injection and source modification restrictions in `AGENTS.md`.

See `docs/GITLAB_SETUP.md` for additional setup gates and `docs/TEST_MATRIX.md` for the evaluation plan.

## License

MIT.

## Creating a real vulnerable merge request (controlled demo)

After the secure code is committed and GitLab access is confirmed, create a disposable branch:

```sh
git switch -c demo/m01-invoice-leak
python scripts/prepare_m01_branch.py --acknowledge-synthetic
python -m pytest -q tests/baseline       # should pass
python -m pytest -q tests/isolation      # should fail before Duo remediation
git add app/main.py
git commit -m "demo: reproduce missing tenant predicate M01"
git push -u origin demo/m01-invoice-leak
```

Create a merge request targeting the protected default branch. The CI isolation gate **must be red** before any patch is applied. Assign the GitLab Duo flow service account as reviewer to start remediation. The automation must never merge an unverified branch. This helper refuses to run on the default branch and does not push anything by itself.

## Execution Pack 02 — Live GitLab Gate 0 (October 13, 2026)

First run the static configuration and CI safety checks:

```sh
make gate0-local
```

**Safe smoke before autonomous code edits:** In `AI > Flows > New flow`, register
`.gitlab/duo/flows/gate0-smoke.yaml` as **TENANTPROOF Gate 0 Smoke** and enable
ONLY **Assign reviewer**. Assign its service account as reviewer on a harmless
human-created MR. Inspect `AI > Sessions`; success means the real agent read
this MR and posted exactly one note containing
`TENANTPROOF_GATE0_MR_READ_WRITE_OK`. This is **not** evidence of a code push.
Do not create a second trigger for the same flow during this smoke test.

Optionally inspect the remote project and MR without changing anything:

```sh
export GITLAB_TOKEN="<your short-lived GitLab read_api token>"
python scripts/gitlab_gate0.py --project "your-group/tenantproof" --mr 1
unset GITLAB_TOKEN
```

The script writes a sanitized local report under `evidence/live/` which is
ignored by git. Never commit tokens, tokens in URLs, or private MR content.
Normal GitLab project and pipeline REST responses do **not** prove Duo executed.
Evidence of Duo execution MUST be inspected under `AI > Sessions`.

After smoke succeeds, register the main flow from
`.gitlab/duo/flows/tenantproof.yaml` and select **Assign reviewer** only.
Open the disposable M01 MR and assign that flow's account as reviewer.
The target `isolation-gate` should be red before the agent patches code. This
pack has NOT implemented Hands-off automatic merge, Cloud Run provisioning,
or autonomous release, and it makes no such claim.

See `docs/GATE0_LIVE_RUNBOOK.md` for UI steps and the evidence gate.
