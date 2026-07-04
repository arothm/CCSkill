# Testing harness — shared playbook for all test agents

Every testing agent (`frontend-test`, `frontend-e2e`, `frontend-designer`,
`backend-test`, `backend-e2e`, `security-test`) follows this playbook so they
verify with real evidence instead of reasoning about the code, stay
zero-dependency, and don't reinvent the same plumbing each run. It adapts the
patterns proven by Anthropic's `webapp-testing` skill to the fleet's principles.

## Policy 1 — Prefer the project's own runner; generate ad-hoc only as fallback

The project's maintained test suite is repeatable and trusted; generated
automation is not. So:

1. **Run what the project already has first** — the test/e2e commands detected
   in Step 1 (Jest/Vitest/Playwright/Cypress/pytest/etc.). This is the primary
   signal.
2. **Generate ad-hoc automation only when there is no suite** for what you need
   to verify, or to reproduce a specific bug. Label generated-automation results
   as such so they aren't mistaken for the project's own guarantees.

This directly answers the QA caveat: skills are good at ad-hoc generated
checks, but repeatable suites are better when they exist — so use them when they
exist.

## Policy 2 — Zero-dependency; browser automation via MCP (opt-in)

The skill installs nothing. Two consequences:

- **Server lifecycle** uses the bundled `scripts/with_server.py` (Python
  standard library only). It starts one or more servers, waits for their ports,
  runs your command, and tears them down. Run it with `--help`, then invoke it
  as a **black box** — do not read its source into your context (that wastes
  tokens; the script exists precisely so you don't have to).
- **Browser control** (rendering, clicking, screenshots, console logs) is done
  through a **Playwright/browser MCP if one is connected** — not a bundled
  Playwright install. Check for an available browser/Playwright MCP first.
  - If present: drive the browser through the MCP tools.
  - If absent: do **not** fabricate rendered results. Run the project's own
    headed/e2e suite if it has one, otherwise fall back to static code analysis
    and clearly mark those findings **"unverified (no browser available)"** so
    the coordinator and user know they weren't confirmed live. Note the missing
    MCP as a finding — knowing you couldn't render is useful information.

## Policy 3 — Reconnaissance-then-action (for anything browser-driven)

The most common browser-automation bug is acting before the page is ready. So:

1. **Navigate**, then **wait for the network to go idle** (equivalent of
   Playwright's `networkidle`) before you inspect anything on a dynamic app.
2. **Inspect the rendered state** — screenshot and/or read the DOM — to discover
   the real selectors.
3. **Act** using the discovered selectors, with explicit waits.

Decision tree for locating selectors:

```
Is the target static HTML?
  ├─ Yes → read the HTML file directly to get selectors
  │         └─ if that's incomplete, treat it as dynamic (below)
  └─ No (dynamic) → is the server already running?
       ├─ No  → use scripts/with_server.py to start it, then reconnoiter
       └─ Yes → navigate → wait for network idle → screenshot/inspect → act
```

## Policy 4 — Capture evidence to `.fleet/log/<run-id>/`

"Never assume" means your claims should be backed by artifacts the user can
open. For each run, save into `.fleet/log/<run-id>/` (git-ignored):

- **Screenshots** at the relevant states (and, for the designer, one per
  breakpoint).
- **Console logs** and any Playwright/e2e **traces** the runner produces.
- **Scanner output** (from `scripts/run_scanners.py`) for the security agent.

Reference the artifact path in the finding, e.g. `Fix: … (see
.fleet/log/<run-id>/checkout-500.png)`. A finding with an artifact is verified;
one without is, at best, "likely."

## Policy 5 — Cache harness facts in memory

Discovering how to start the app, which selectors matter, where the e2e runner
lives, and whether a browser MCP is available costs tokens. Record these as a
**Memory delta** so the next run inherits them instead of rediscovering:

- server start command(s) + ports and readiness URL
- e2e/test runner location and invocation
- stable selectors for critical flows
- browser MCP availability
- design tokens / breakpoints (for the designer)

Verify a cached fact still holds if the relevant files changed since it was
recorded (check the diff, not a hunch) — stale harness facts are worse than
none.

## Security-specific: the scanner runner

`security-test` uses `scripts/run_scanners.py` (stdlib only, installs nothing).
It detects which scanners are already on PATH (`npm audit`, `pip-audit`,
`cargo audit`, `osv-scanner`, `semgrep`, `bandit`, `gitleaks`, `trufflehog`),
runs the ones that fit the repo, and prints a normalized summary to triage.
Run it with `--help` first, invoke as a black box, save output to the run log —
then **confirm each reported issue against the real code** before reporting it,
because scanners produce false positives (never-assume). If no scanner is
installed, it says so; fall back to manual review and state that, don't
fabricate results.
