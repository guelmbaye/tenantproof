"""Read-only GitLab gate 0 diagnostic via REST API; never modifies a project.

GITLAB_TOKEN is provided in the environment and never written to the report.
Makes only GET requests to API endpoints. The gate cannot verify Duo sessions;
those are checked in GitLab's AI > Sessions UI.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def api_get(base, token, route):
    url=base.rstrip('/')+'/api/v4/'+route.lstrip('/')
    req=Request(url, headers={'PRIVATE-TOKEN':token,'Accept':'application/json'},method='GET')
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8')),None
    except HTTPError as e:
        return None, 'HTTP_'+str(e.code)
    except (URLError,TimeoutError,ValueError) as e:
        return None, 'NETWORK_OR_RESPONSE_ERROR_'+type(e).__name__


def evaluate(project, mr, base, token, getter=api_get):
    encoded=quote(str(project),safe='')
    result={'schema_version':1,'checked_at':datetime.now(timezone.utc).isoformat(),
            'gitlab_base':base,'project':str(project),'mr_iid':mr,
            'remote_checked':True,'gitlab_duo_flow_executed':None,'autonomous_patch':None,
            'autonomous_merge':None,'runtime_release_verified':None,'checks':{},'overall':'INCONCLUSIVE'}
    info,err=getter(base,token,f'projects/{encoded}')
    if err:
        result['checks']['project_api']={'status':'FAIL','error':err}
        return result
    result['checks']['project_api']={'status':'PASS','web_url':info.get('web_url'),
                                     'default_branch':info.get('default_branch'),
                                     'visibility':info.get('visibility')}
    if info.get('visibility') != 'public':
        result['checks']['project_visibility']={'status':'FAIL','reason':'Hackathon requires a public repo'}
    else:
        result['checks']['project_visibility']={'status':'PASS'}
    branch=info.get('default_branch')
    if branch:
        protected,protect_error=getter(base,token,f'projects/{encoded}/protected_branches/{quote(branch,safe="")}')
        result['checks']['default_branch_protection']={
            'status':'INCONCLUSIVE' if protect_error else 'PASS',
            'is_protected':not bool(protect_error),
            'error':protect_error,
            'note':'A protected branch alone does not guarantee required pipeline gates.'}
    if mr is not None:
        mr_info,mr_err=getter(base,token,f'projects/{encoded}/merge_requests/{mr}')
        if mr_err:
            result['checks']['mr_access']={'status':'FAIL','error':mr_err}
        else:
            result['checks']['mr_access']={'status':'PASS','url':mr_info.get('web_url'),
                                          'state':mr_info.get('state'),
                                          'source_branch':mr_info.get('source_branch'),
                                          'target_branch':mr_info.get('target_branch'),
                                          'sha':mr_info.get('sha'),
                                          'merge_status':mr_info.get('detailed_merge_status')}
            pipelines,p_err=getter(base,token,f'projects/{encoded}/merge_requests/{mr}/pipelines?per_page=10')
            result['checks']['mr_pipelines']={
                'status':'INCONCLUSIVE' if p_err else ('PASS' if pipelines else 'FAIL'),
                'pipelines':[{ 'id':p.get('id'),'status':p.get('status'),'sha':p.get('sha'),
                               'web_url':p.get('web_url')} for p in (pipelines or [])[:5]],
                'error':p_err}
    # Gate0 is never allowed to infer an actual Duo run from ordinary GitLab REST.
    result['overall']='REMOTE_READABLE__DUO_UNVERIFIED'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',required=True,help='GitLab namespace/name or numeric project ID')
    p.add_argument('--mr',type=int)
    p.add_argument('--base',default='https://gitlab.com')
    p.add_argument('--output',default='evidence/live/gate0.json')
    args=p.parse_args()
    parsed=urlparse(args.base)
    if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        p.error('--base must be an HTTPS GitLab instance origin without credentials/query')
    token=os.getenv('GITLAB_TOKEN','')
    if not token:
        p.error('Set GITLAB_TOKEN in environment (never pass the token as a command-line argument)')
    result=evaluate(args.project,args.mr,args.base,token)
    output=Path(args.output).resolve()
    allowed=(Path.cwd()/'evidence/live').resolve()
    if not output.is_relative_to(allowed):
        p.error('For safety output must reside under evidence/live/')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    print('Saved local-only diagnostic:',output)
    if result['checks'].get('project_api',{}).get('status') != 'PASS':
        sys.exit(2)

if __name__=='__main__':
    main()
