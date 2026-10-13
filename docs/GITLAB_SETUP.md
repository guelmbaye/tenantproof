# GitLab integration gate and operational runbook

**Gate 0 — external steps requiring real GitLab account**

1. Register for GitLab Transcend contributor access. Confirm the correct hackathon group/project.
2. Check custom flow access, credits and project role. GitLab docs indicate custom flows are broadly available but trigger entitlements depend on tier; actual provisioned access is decisive.
3. Push `.gitlab/duo/agent-config.yml` to the default branch. Do NOT edit setup scripts from a suspicious MR: they execute before sandbox restrictions and can access tokens.
4. Register the custom flow YAML via **AI > Flows**; enable the flow in the project.
5. Configure **Assign reviewer** trigger for the flow service account. This yields an MR IID in context:goal. Do not use MR-created event until adapting the goal parser.
6. Test with a harmless MR first and preserve session URL/job ID. Confirm `run_command`, git write and push behavior.
7. Make required CI jobs mandatory for merge: `unit-tests`, `isolation-gate`, `security-check`. Protect default branch, reject direct pushes, restrict merge to approved automation identity. Ensure agent cannot edit protected gate configurations.
8. Run M01 in a disposable `demo/m01-*` branch using `scripts/prepare_m01_branch.py --acknowledge-synthetic`; never deploy an intentionally vulnerable version.
9. Validate automatic merge support; the included flow only prepares patch and evidence — **there is no automated merge implementation in this bootstrap**.
10. Enable deployment only after WIF, Cloud SQL and synthetic token generation are verified. Preserve commit SHA, image digest and HTTP probes.

Before the main remediation flow, use `docs/GATE0_LIVE_RUNBOOK.md` and the
read/comment smoke flow. A successful comment is NOT a proof of source push.

## GO / NO-GO

- **GO platform**: completed Duo session with actual tool calls + CI jobs run.
- **GO vertical slice**: agent produces executable regression test and repair on actual MR and current CI blocks unsafe version.
- **GO Hands-off**: verified autonomous merge and deployment with no intermediate human action.
- **NO-GO**: only a CI script triggers, agent cannot write, gate is bypassable or evidence links are missing.

## Docs

- https://docs.gitlab.com/user/duo_agent_platform/flows/custom/
- https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/
- https://docs.gitlab.com/user/duo_agent_platform/triggers/
- https://docs.gitlab.com/user/duo_agent_platform/flows/execution/
- https://docs.gitlab.com/user/duo_agent_platform/flows/claude-edit-v1-flow-registry/
