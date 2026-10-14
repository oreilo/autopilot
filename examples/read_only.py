import asyncio
import os
from oreilo_autopilot import AutoPilot, AgentConfig
from oreilo_autopilot.provider import OpenAICompatibleProvider

async def main():
    provider = OpenAICompatibleProvider(os.getenv("AUTOPILOT_MODEL", "gpt-4.1-mini"), os.environ["AUTOPILOT_API_KEY"])
    agent = AutoPilot(provider, AgentConfig(allowed_domains=("example.com",), max_steps=8))
    result = await agent.run("Summarize the page and report its title. Do not interact with controls.", "https://example.com")
    print(result)

asyncio.run(main())
