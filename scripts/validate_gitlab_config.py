"""Static safety checks for the GitLab Duo/CI configuration.

Not a substitute for GitLab's server-side v1 schema validator or remote
branch-protection rules. Does not contact any network service.
"""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
FLOW_PATHS = [ROOT / '.gitlab/duo/flows/gate0-smoke.yaml', ROOT / '.gitlab/duo/flows/tenantproof.yaml']
ALLOWED_TOOLS = {
    'get_merge_request', 'read_file', 'list_dir', 'grep', 'edit_file',
    'create_file_with_contents', 'run_command', 'create_merge_request_note',
    'find_files', 'get_project', 'create_commit',
}


def validate_flow(path):
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    problems = []
    if not isinstance(data, dict):
        return [f'{path.name}: root is not a mapping']
    if data.get('version') != 'v1' or data.get('environment') != 'ambient':
        problems.append('version must be v1 and environment ambient')
    for restricted in ('name', 'description', 'product_group'):
        if restricted in data:
            problems.append('restricted top-level field: '+restricted)
    if data.get('coding_environment', 'full') != 'full':
        problems.append('source-editing demo must use full coding environment')
    comps = data.get('components', [])
    prompts = data.get('prompts', [])
    if not isinstance(comps, list) or not comps or not isinstance(prompts, list):
        return [f'{path.name}: missing components or prompts']
    pnames = {p.get('prompt_id') for p in prompts}
    cnames = {c.get('name') for c in comps}
    for component in comps:
        if component.get('type') != 'AgentComponent':
            problems.append('unexpected component type')
        if component.get('prompt_id') not in pnames:
            problems.append('unresolved prompt id')
        if component.get('require_tool_approval') is True:
            problems.append('tool approval would defeat Hands-off target')
        keys = [t if isinstance(t, str) else next(iter(t)) for t in component.get('toolset', [])]
        if not set(keys) <= ALLOWED_TOOLS:
            problems.append('tools not in documented allowlist: '+str(set(keys)-ALLOWED_TOOLS))
        aliases = {i.get('as') for i in component.get('inputs', []) if isinstance(i, dict)}
        if not {'project_id','mr_iid'} <= aliases:
            problems.append('assign reviewer context must contain project_id and mr_iid')
    for prompt in prompts:
        template = prompt.get('prompt_template', {})
        if template.get('placeholder') != 'history' or 'unit_primitives' not in prompt:
            problems.append('prompt missing history placeholder or unit_primitives')
        user = template.get('user','')
        if '{{ project_id }}' not in user or '{{ mr_iid }}' not in user:
            problems.append('prompt not wired to both MR identifiers')
    if data.get('flow',{}).get('entry_point') not in cnames:
        problems.append('invalid entry_point')
    if not data.get('routers') or not all(r.get('from') in cnames for r in data['routers']):
        problems.append('missing or malformed router')
    return [f'{path.name}: {p}' for p in problems]


def validate_agent_config():
    path=ROOT/'.gitlab/duo/agent-config.yml'
    data=yaml.safe_load(path.read_text(encoding='utf-8'))
    issues=[]
    if not isinstance(data,dict):
        return ['agent-config not a mapping']
    for cmd in data.get('setup_script',[]):
        if any(x in cmd for x in ('-r requirements.txt', 'bash scripts/', 'sh scripts/', 'curl | sh', 'wget | sh')):
            issues.append('untrusted script/dependency invocation in setup_script')
    return issues


def validate_ci():
    cfg=yaml.safe_load((ROOT/'.gitlab-ci.yml').read_text(encoding='utf-8'))
    issues=[]
    for job in ('unit-tests','isolation-gate','security-check'):
        value=cfg.get(job)
        if not isinstance(value,dict):
            issues.append('mandatory CI job missing: '+job)
            continue
        if value.get('allow_failure',False) is not False:
            issues.append(job+' is allow_failure')
        if 'rules' in value or 'only' in value or 'except' in value:
            issues.append(job+' can be skipped by job-level conditions')
    script=cfg.get('isolation-gate',{}).get('script',[])
    if not any('pytest' in str(s) and 'tests/isolation' in str(s) for s in script):
        issues.append('isolation gate does not run isolation suite')
    deploy=cfg.get('cloudrun-deploy',{})
    if not any('DEPLOY_ENABLED' in str(r.get('if','')) for r in deploy.get('rules', [])):
        issues.append('deployment must be explicitly opt-in')
    return issues


def main():
    issues=[]
    for path in FLOW_PATHS:
        issues += validate_flow(path)
    issues += validate_agent_config()
    issues += validate_ci()
    if issues:
        print('\n'.join('FAIL: '+x for x in issues))
        sys.exit(1)
    print('PASS: local static validation for Duo YAML, setup and critical CI job declarations')
    print('NOTICE: remote GitLab schema, permissions, trigger, runner and pushes remain UNVERIFIED')

if __name__ == '__main__':
    main()
