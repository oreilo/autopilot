# AutoPilot v1.1 - Extended Modules

AutoPilot offers an LLM-driven Playwright execution loop with an allowlisted browser context, an explicit action policy, a CLI, an API, and developer integrations.

## Task history
`TaskStore('artifacts/autopilot.db')` stores tasks, transitions, events, and results in SQLite with WAL mode. It is available as an SDK component. The API does not automatically enqueue or persist tasks in this store.

## Deterministic workflows
`Workflow.load('workflow.json')` loads a typed JSON workflow. Use `execute_workflow(workflow, browser, domains, policy)` to replay it with the same browser guardrails.

## Structured extraction
`extract_html(html, base_url)` extracts headings, links, tables, and visible text. `export_records(records, 'report.csv')` exports JSON or CSV. The browser supports `extract_structured` actions.

## Tabs and navigation
New actions: `wait`, `back`, `tab_new`, `tab_switch`, `extract_structured`. Browser pages share one isolated browser context.

## Scheduling and batches
`Scheduler` is an in-process interval runner, not a distributed scheduler. `run_batch` provides bounded concurrency for independent tasks.

## Safety
The action policy blocks interactions by default and requires separate authorization for actions whose selector, reason, or value matches sensitive terms. **Heuristics cannot reliably detect all sensitive operations.** Always supervise consequential workflows. Allowlisted domains and URL validation are not a complete network sandbox. Browser resource routing should be supplemented by egress controls for hostile sites.

## Known limitations
No visual reasoning provider, distributed workers, persistent browser session recovery, production approval service, or automated proof that an LLM's final answer is correct. `verify_page` provides explicit page assertions for applications to invoke. API tasks run synchronously and may time out behind a reverse proxy.
