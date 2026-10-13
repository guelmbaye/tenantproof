from scripts.validate_gitlab_config import validate_flow, validate_agent_config, validate_ci, FLOW_PATHS
from scripts.gitlab_gate0 import evaluate

def test_flows_have_supported_local_shape():
    for path in FLOW_PATHS:
        assert validate_flow(path)==[]

def test_no_untrusted_setup_scripts():
    assert validate_agent_config()==[]

def test_critical_gates_present():
    assert validate_ci()==[]

def test_gitlab_readonly_diagnostic_never_infers_duo_success():
    calls=[]
    def fake_get(base,token,route):
        calls.append(route)
        if '/protected_branches/' in route: return {'name':'main'},None
        if '/merge_requests/3/pipelines' in route:
            return [{'id':89,'status':'success','sha':'abc','web_url':'https://gitlab.com/a/b/-/pipelines/89'}],None
        if '/merge_requests/3' in route:
            return {'web_url':'https://gitlab.com/a/b/-/merge_requests/3','sha':'abc','state':'opened'},None
        return {'web_url':'https://gitlab.com/a/b','visibility':'public','default_branch':'main'},None
    result=evaluate('a/b',3,'https://gitlab.com','example',getter=fake_get)
    assert result['checks']['project_api']['status']=='PASS'
    assert result['checks']['mr_pipelines']['status']=='PASS'
    assert result['gitlab_duo_flow_executed'] is None
    assert result['overall']=='REMOTE_READABLE__DUO_UNVERIFIED'
    assert all('example' not in x for x in str(result).split())
    assert len(calls)==4
