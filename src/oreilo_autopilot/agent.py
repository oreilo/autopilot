import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from .models import Action, StepRecord
from .security import PolicyError, require_approval, validate_url
from .browser import Browser
from .redaction import redact
from .policies import ActionPolicy

@dataclass
class AgentConfig:
    allowed_domains: tuple[str, ...]
    max_steps: int = 20
    headed: bool = False
    artifact_dir: str = "artifacts"
    approve_interactions: bool = False
    max_failures: int = 3
    allow_sensitive: bool = False
    max_actions: int = 50

@dataclass
class AgentResult:
    run_id: str
    status: str
    answer: str
    steps: list[dict] = field(default_factory=list)
    error: str | None = None

class AutoPilot:
    def __init__(self, provider, config: AgentConfig):
        if not config.allowed_domains:
            raise ValueError("At least one allowed domain is required")
        if config.max_steps < 1 or config.max_steps > 200:
            raise ValueError("max_steps must be between 1 and 200")
        self.provider, self.config = provider, config

    async def run(self, task: str, start_url: str) -> AgentResult:
        validate_url(start_url, self.config.allowed_domains)
        run_id = uuid4().hex
        steps, failures = [], 0
        status, answer, error = "step_limit", "", None
        try:
            async with Browser(self.config.allowed_domains, self.config.headed, self.config.artifact_dir) as browser:
                await browser.execute(Action(kind="navigate", url=start_url), 0)
                for index in range(1, self.config.max_steps + 1):
                    observation = (await browser.observe(index)).model_dump()
                    action = await self.provider.decide(task, observation, steps)
                    try:
                        if action.kind == "navigate": validate_url(action.url or "", self.config.allowed_domains)
                        ActionPolicy(self.config.approve_interactions,self.config.allow_sensitive,self.config.max_actions).check(action, observation, index-1)
                        if action.kind == "finish":
                            status, answer = "completed", action.answer or "Task marked complete by model"
                            steps.append(StepRecord(step=index, action=action, url=observation["url"], outcome="completed").model_dump())
                            break
                        detail = await browser.execute(action, index)
                        steps.append(StepRecord(step=index, action=action, url=browser.page.url, outcome="ok", detail=redact(detail[:2000])).model_dump())
                        failures = 0
                    except (Exception) as exc:
                        failures += 1
                        steps.append(StepRecord(step=index, action=action, url=observation["url"], outcome="failed", detail=redact(str(exc)[:500])).model_dump())
                        if isinstance(exc, PolicyError):
                            status, error = "blocked", redact(str(exc)); break
                        if failures >= self.config.max_failures:
                            status, error = "failed", redact(str(exc)); break
                        await asyncio.sleep(min(2 ** failures, 8))
        except Exception as exc:
            status, error = "failed", redact(str(exc))
        result = AgentResult(run_id=run_id, status=status, answer=answer, steps=steps, error=error)
        output = Path(self.config.artifact_dir) / "runs"
        output.mkdir(parents=True, exist_ok=True)
        (output / f"{run_id}.json").write_text(json.dumps({**result.__dict__, "timestamp": datetime.now(timezone.utc).isoformat()}, indent=2, default=str), encoding="utf-8")
        return result
