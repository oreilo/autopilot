"""Replayable, deterministic workflows for developers and regression testing."""
import json
from pathlib import Path
from pydantic import BaseModel, Field
from .models import Action
from .security import validate_url
from .policies import ActionPolicy

class Workflow(BaseModel):
    name: str=Field(min_length=1)
    description: str=''
    start_url: str
    actions: list[Action]=Field(min_length=1,max_length=200)
    @classmethod
    def load(cls,path): return cls.model_validate(json.loads(Path(path).read_text(encoding='utf-8')))
    def save(self,path): Path(path).write_text(self.model_dump_json(indent=2),encoding='utf-8')

async def execute_workflow(workflow,browser,domains,policy=None):
    policy=policy or ActionPolicy()
    validate_url(workflow.start_url,domains)
    await browser.execute(Action(kind='navigate',url=workflow.start_url),0)
    results=[]
    for i,action in enumerate(workflow.actions,1):
        policy.check(action,{},i-1)
        if action.kind=='navigate': validate_url(action.url or '',domains)
        detail=await browser.execute(action,i)
        results.append({'step':i,'action':action.kind,'detail':detail})
        if action.kind=='finish': break
    return results
