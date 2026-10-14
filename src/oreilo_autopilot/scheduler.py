"""Simple recurring job runner intended for single-process deployments."""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class Schedule:
    name: str
    interval_seconds: int
    task: str
    start_url: str
    allowed_domains: tuple[str,...]
    def __post_init__(self):
        if self.interval_seconds<60: raise ValueError('Minimum schedule interval is 60 seconds')

class Scheduler:
    def __init__(self,run): self.run=run;self.jobs={};self._running=False
    def add(self,job:Schedule): self.jobs[job.name]=job
    async def serve(self,stop:asyncio.Event):
        next_run={name:0.0 for name in self.jobs}
        loop=asyncio.get_running_loop()
        while not stop.is_set():
            now=loop.time()
            for name,job in list(self.jobs.items()):
                if now>=next_run.get(name,0):
                    next_run[name]=now+job.interval_seconds
                    await self.run(job)
            try: await asyncio.wait_for(stop.wait(),timeout=1)
            except asyncio.TimeoutError: pass
