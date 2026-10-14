"""Concurrency-limited execution of independent research/browser tasks."""
import asyncio
from dataclasses import dataclass

@dataclass
class BatchTask:
    task: str
    url: str

async def run_batch(agent_factory,tasks,concurrency=3):
    if not 1<=concurrency<=20: raise ValueError('concurrency must be 1..20')
    sem=asyncio.Semaphore(concurrency)
    async def worker(item):
        async with sem:
            try: return await agent_factory().run(item.task,item.url)
            except Exception as exc: return {'status':'failed','error':str(exc)}
    return await asyncio.gather(*(worker(t) for t in tasks))
