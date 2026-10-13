# Gate 0 — Live GitLab validation runbook (2026-10-13)

## Local preflight

1. `make gate0-local`: check both flow configurations, agent setup and CI gates.
2. `make test`: secure source remains green.
3. `make baseline`: M01 mutation is isolated; conventional tests green, boundary tests red.
4. Configure protected default branch / successful pipelines required in GitLab UI.
5. The flow setup does NOT install untrusted MR-editable dependencies.

## External smoke test — no code edits

1. Commit bootstrap files to the *default* branch of a **public MIT** GitLab project.
2. Verify `Settings > General > GitLab Duo`, group access/credits and a functioning
   Duo runner; hosted runner or compatible `gitlab--duo` self-hosted runner.
3. Navigate to `AI > Flows > New flow` (Maintainer/Owner needed).
4. Paste `.gitlab/duo/flows/gate0-smoke.yaml`, save as `TENANTPROOF Gate 0 Smoke`.
5. Enable it in the project; choose **Assign reviewer** trigger only.
6. Create a harmless MR as a human. Assign the smoke flow's service account reviewer.
7. Visit `AI > Sessions`: inspect the **real** flow execution and tool logs.
8. Confirm a comment containing the literal marker
   `TENANTPROOF_GATE0_MR_READ_WRITE_OK` on that MR.
9. Record MR URL, Duo session URL, job URL and UTC date (do not fabricate).
10. Run `python scripts/gitlab_gate0.py --project namespace/repo --mr IID`
    with `GITLAB_TOKEN` set if read-only remote API diagnostics are useful.

**PASS G0a:** an agent session with successful MR read and MR note; ordinary CI
pipelines, smoke YAML or local tests alone are not sufficient.

**FAIL:** setup invalid, runner stuck, missing GitLab Duo entitlement, API tools
unavailable, missing service-account permission, or no actual comment.

## External patch test — requires live source writes

1. Register and enable the main flow `tenantproof.yaml` using Assign reviewer.
2. Protect `.gitlab-ci.yml`, `.gitlab/duo/`, `scripts/check_release_policy.py`
   and any release policy files with appropriate project access governance.
3. Create M01 MR via `scripts/prepare_m01_branch.py --acknowledge-synthetic`
   on a clean `demo/m01-*` branch.
4. Verify the MR source pipeline fails `isolation-gate` and cannot merge.
5. Assign the main flow service account as reviewer once.
6. Inspect its session: input MR, actual tests, source diff and commit, git push.
7. Confirm the MR has a new head SHA and the new pipeline passes both boundary
   tests and the original authorized-access tests.
8. Record exact URLs in an external evidence manifest. Distinguish a patch
   suggestion from an actual pushed commit.

**PASS G0b:** real agent produced a test, applied a patch, pushed it to MR
source branch and it passed independent CI. G0a by itself is *not* G0b.

## Release prerequisite, not implemented in Pack 02

Before Hands-off claim, the project must additionally demonstrate authorized
automatic merging of a VERIFIED SHA, a deployment pipeline producing a pinned
image digest, and post-deployment HTTP probes. A `success` status for a CI job
or an agent final response does not demonstrate this.

## Important constraints

- GitLab Custom Flows use flow registry v1; final server-side schema validation
  happens in the GitLab UI, beyond our local structural check.
- `agent-config.yml` is taken from the DEFAULT branch and its setup scripts
  run in a privileged phase. Avoid installing requirements from editable MR code.
- Trigger type `Assign reviewer` passes MR IID as `context:goal`.
- Custom flows require project enablement and permissions. Users may encounter
  runner or GitLab Credits issues; record the actual error and classify as
  INCONCLUSIVE rather than claiming success.
- GitLab normal REST API metadata cannot establish Duo session/tool outcomes.

Sources:
- https://docs.gitlab.com/user/duo_agent_platform/flows/custom/
- https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/
- https://docs.gitlab.com/user/duo_agent_platform/flows/execution/
- https://docs.gitlab.com/user/duo_agent_platform/triggers/
