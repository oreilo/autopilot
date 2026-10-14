# Architecture

CLI/API -> AutoPilot loop -> model provider -> validated Action -> security checks -> Playwright Browser -> observation -> loop. Per-run JSON traces saved to artifacts/runs. Browser contexts are ephemeral and downloads disabled. DNS and allowlist checks happen at navigation and routed requests. All model-proposed interaction actions are gated by an explicit run-level approval flag. API never enables this flag.

## Extension points

Implement `async decide(task, observation, history) -> Action` to use a custom provider. For deterministic testing, inject a fake provider. Extend Browser.execute and Action together to add new action types, with explicit permission checks. Use external task queues for production-scale execution.
