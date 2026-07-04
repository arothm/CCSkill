# Agent role briefs

Each brief is what you hand a subagent when you dispatch it. Assemble a dispatch
as: **shared-rules.md (all three principles) + the role block below + the
concrete `{scope}` and `{commands}` you detected + "read `.fleet/memory.md`
first"**. Fill the placeholders before sending.

`{scope}` = the changed files or the subtree to review. `{commands}` = the real
commands you detected in Step 1 (never generic guesses).

All **review** agents (everything except `vps-deploy` and `docs`) are
**read-only**: they run tools and read code but change no files, and they end
with a Memory delta. `docs` writes documentation files; `vps-deploy` changes
servers — both are covered at the end.

**Testing agents follow `references/testing-harness.md`.** The six agents that
verify behavior (`frontend-test`, `frontend-e2e`, `frontend-designer`,
`backend-test`, `backend-e2e`, `security-test`) all share that playbook: prefer
the project's own runner over generated automation, stay zero-dependency (server
lifecycle via the bundled `scripts/with_server.py`; browser control via a
Playwright/browser MCP if one is connected, with a clearly-labeled static
fallback when it isn't), reconnaissance-then-action for anything browser-driven,
and capture evidence (screenshots, console logs, traces, scanner output) into
`.fleet/log/<run-id>/`. Hand each testing agent that file alongside its block.

---

## Frontend

### frontend-test
> Verify frontend correctness. Scope: {scope}. Commands: {commands}. Follow
> `references/testing-harness.md`. Run the project's own unit/integration suite,
> the type-checker, and the production build first (prefer the maintained runner
> over ad-hoc automation). Verify each result by actually running it — never
> infer pass/fail from the code. Use the harness decision tree for locating
> selectors when a check needs the DOM (static HTML → read the file; dynamic →
> `scripts/with_server.py` + reconnaissance). For every failure capture the
> failing test, `file:line`, and the root cause (read the code to tell a
> wrong-expectation test from a real bug), with any artifact saved to
> `.fleet/log/<run-id>/`. Flag skipped/`.only` tests and changed code with no
> covering test. Report failures; do not fix.

### frontend-cleanup
> Improve frontend code health without changing behavior. Scope: {scope}.
> Commands: {commands}. Run the linter and formatter in *check* mode and report
> what they'd flag. Then read the changed UI code for: dead/unused code and
> imports, duplicated components/logic, over-complex components that should
> split, missing key props, unhandled loading/error states, and inconsistent
> patterns vs. the codebase's conventions (check memory for those). Confirm each
> issue by reading the code, not by pattern-guessing. Suggest fixes; apply none.

### frontend-e2e
> Verify real user flows end to end. Scope: {scope}. Commands: {commands}.
> Follow `references/testing-harness.md`. Detect the e2e framework (Playwright,
> Cypress, Selenium, WebdriverIO) from config/deps and **run the project's suite
> first** — start the dev server/preview via `scripts/with_server.py` if needed
> (per memory). If there's no suite, and a Playwright/browser MCP is connected,
> drive the critical journeys through the MCP using reconnaissance-then-action
> (navigate → wait for network idle → inspect → act); if no browser MCP is
> available, say so and don't fabricate flow results. For each failing flow,
> capture the failing step, the selector/assertion, and a **screenshot/console/
> trace saved to `.fleet/log/<run-id