import asyncio
import json
import os
import typer
from .agent import AutoPilot, AgentConfig
from .provider import OpenAICompatibleProvider

app = typer.Typer(help="OREiLO AutoPilot - autonomous browser agent")

@app.command()
def run(task: str = typer.Option(..., help="Natural language objective"), start_url: str = typer.Option(...), allow_domain: list[str] = typer.Option(...), model: str = typer.Option("gpt-4.1-mini"), headed: bool = False, approve_interactions: bool = False, max_steps: int = 20):
    key = os.getenv("AUTOPILOT_API_KEY")
    if not key: raise typer.BadParameter("Set AUTOPILOT_API_KEY")
    provider = OpenAICompatibleProvider(model, key, os.getenv("AUTOPILOT_BASE_URL", "https://api.openai.com/v1"))
    config = AgentConfig(tuple(allow_domain), max_steps=max_steps, headed=headed, approve_interactions=approve_interactions)
    result = asyncio.run(AutoPilot(provider, config).run(task, start_url))
    typer.echo(json.dumps(result.__dict__, indent=2, default=str))
    if result.status != "completed": raise typer.Exit(code=1)

if __name__ == "__main__": app()
