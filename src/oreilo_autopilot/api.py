import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from .agent import AutoPilot, AgentConfig
from .provider import OpenAICompatibleProvider

app = FastAPI(title="OREiLO AutoPilot API", version="1.0.0")

class TaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=4000)
    start_url: str
    allowed_domains: list[str] = Field(min_length=1)
    max_steps: int = Field(default=20, ge=1, le=200)
    model: str = "gpt-4.1-mini"

@app.get("/health")
async def health(): return {"status": "ok"}

@app.post("/run")
async def run_task(request: TaskRequest, x_api_key: str | None = Header(default=None)):
    expected = os.getenv("AUTOPILOT_SERVER_KEY")
    if not expected or x_api_key != expected:
        raise HTTPException(401, "Invalid API key")
    model_key = os.getenv("AUTOPILOT_API_KEY")
    if not model_key: raise HTTPException(503, "Model provider is not configured")
    provider = OpenAICompatibleProvider(request.model, model_key, os.getenv("AUTOPILOT_BASE_URL", "https://api.openai.com/v1"))
    agent = AutoPilot(provider, AgentConfig(tuple(request.allowed_domains), max_steps=request.max_steps, approve_interactions=False))
    return (await agent.run(request.task, request.start_url)).__dict__
