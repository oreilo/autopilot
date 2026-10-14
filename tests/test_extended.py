import asyncio
import json
import pytest
from oreilo_autopilot.storage import TaskStore
from oreilo_autopilot.extraction import extract_html,export_records
from oreilo_autopilot.policies import ActionPolicy
from oreilo_autopilot.models import Action
from oreilo_autopilot.security import PolicyError
from oreilo_autopilot.redaction import redact
from oreilo_autopilot.workflows import Workflow
from oreilo_autopilot.batch import run_batch,BatchTask
from oreilo_autopilot.scheduler import Schedule

def test_store_lifecycle(tmp_path):
    db=TaskStore(tmp_path/'runs.db');id=db.create('hello','https://example.com',['example.com'])
    assert db.get(id)['status']=='queued'
    db.transition(id,'completed',{'answer':'ok'})
    assert db.get(id)['result']=={'answer':'ok'}
    db.event(id,'step',{'index':1});assert db.events(id)[0]['data']['index']==1
    assert db.list(status='completed')[0]['id']==id
    with pytest.raises(KeyError):db.get('missing')

def test_extract_and_export(tmp_path):
    data=extract_html('<title>Hi</title><h1>Heading</h1><a href="/about">About</a><table><tr><th>A</th></tr><tr><td>B</td></tr></table>','https://example.com')
    assert data['links'][0]['url']=='https://example.com/about'
    assert data['tables'][0][1]==['B']
    path=tmp_path/'a.json';export_records([data],path)
    assert json.loads(path.read_text())[0]['title']=='Hi'
    export_records([{'a':1}],tmp_path/'a.csv')
    assert 'a' in (tmp_path/'a.csv').read_text()

def test_policy():
    p=ActionPolicy(allow_interactions=True)
    p.check(Action(kind='click',selector='#search'),{})
    with pytest.raises(PolicyError):p.check(Action(kind='click',selector='#delete-account'),{})
    with pytest.raises(PolicyError):p.check(type('A',(),{'kind':'upload','selector':None,'reason':'','value':None})(),{})
    with pytest.raises(PolicyError):ActionPolicy(max_actions=0).check(Action(kind='finish'),{})

def test_workflow_roundtrip(tmp_path):
    w=Workflow(name='sample',start_url='https://example.com',actions=[Action(kind='extract')]);w.save(tmp_path/'w.json')
    assert Workflow.load(tmp_path/'w.json').name=='sample'

def test_redact():
    assert 'secretsecretsecret' not in redact('Bearer secretsecretsecret')
    assert 'abcdabcdabcd' not in redact('api_key=abcdabcdabcd')

def test_schedule():
    with pytest.raises(ValueError):Schedule('test',5,'task','https://example.com',('example.com',))

@pytest.mark.asyncio
async def test_batch():
    class Agent:
        async def run(self,task,url):return task
    results=await run_batch(Agent,[BatchTask('a','url'),BatchTask('b','url')],concurrency=2)
    assert results==['a','b']
