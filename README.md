# OREiLO AutoPilot

**Autonomous browser agent for authorized web tasks.** Open-source Python SDK, CLI, and REST API using Playwright and an OpenAI-compatible model.

AutoPilot observes page text and interactive elements, asks a model to choose a structured action, executes it under a domain and interaction policy, records results, and repeats until completion or an execution limit. This is a real iterative agent, not a hardcoded click sequence.

## Capabilities

- Natural-language objective execution and step-by-step model action selection
- Playwright Chromium automation: navigation, click, fill, press, select, scroll, extract, screenshots
- DOM/text observation, bounded step history, structured JSON actions
- Domain allowlist, public-address checks, network request filtering, disabled downloads, isolated browser contexts
- Interaction approval flag (CLI only); API runs in read-only mode by default
- Retries on failed actions, failure caps, step limits, persistent JSON execution traces
- Python SDK, Typer CLI, authenticated FastAPI endpoint
- Tests, CI, Dockerfile, example, developer and security documentation

## Install

Requires Python 3.10+ and Chromium installation:

```bash
python -m pip install -e '.[dev]'
python -m playwright install chromium
python -m pytest -q
```

Set `AUTOPILOT_API_KEY` for your model provider. Optionally set `AUTOPILOT_BASE_URL` for a compatible API. See `.env.example` (environment variables are not automatically loaded).

## CLI

```bash
autopilot run --task "Summarize the page" --start-url https://example.com --allow-domain example.com
```

For interaction tasks, explicitly pass `--approve-interactions`; **this permits all click/fill/press/select actions within the allowlist**, so use only with trusted tasks and sites. No per-action interactive prompt exists yet.

## Python SDK

See `examples/read_only.py`. Execute `python examples/read_only.py` after installing dependencies.

## REST API

```bash
export AUTOPILOT_SERVER_KEY=change-me
uvicorn oreilo_autopilot.api:app --host 127.0.0.1 --port 8000
```

`POST /run` requires `X-API-Key` and JSON: `{"task":"Summarize the page","start_url":"https://example.com","allowed_domains":["example.com"]}`. The endpoint executes synchronously; it is not a background job system. Do not expose this development API publicly without production hardening.

## Security and limitations

- Treat webpages as untrusted; model prompt instructs the agent not to follow webpage instructions. **Prompt injection is not solved**.
- DNS/IP and domain checks plus request interception are defense-in-depth, **not a hardened network sandbox**. Deploy behind network egress controls for untrusted tasks.
- Browser actions can have real-world effects. Approval flag is coarse-grained, not per-action consent. The API disables interactions.
- No CAPTCHA bypass, stealth, account takeover, payment execution, or credential harvesting features.
- Visual reasoning, multi-agent orchestration, persistent browser session resume, task scheduling, distributed workers, and MCP are **not implemented**.
- Model decisions can be wrong. `finish` is a model claim, not independent task verification.
- Live-browser and provider integration tests require local execution and credentials. Do not assume successful deployment without validation.

## License

MIT. Copyright (c) 2026 OREiLO.

## Support

contact@oreilo.com | https://oreilo.com


## v1.1 Expanded capabilities

Includes SQLite task registry, event history, structured HTML extraction, JSON/CSV export, typed reusable workflows, tab management, bounded parallel batch execution, a lightweight interval scheduler, explicit page verification checks, redaction utilities, and enhanced action policies. See [extended feature guide](docs/EXTENDED_FEATURES.md).

These modules are usable via the Python SDK; the REST API remains synchronous and does not expose every SDK feature.
