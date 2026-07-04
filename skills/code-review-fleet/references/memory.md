# Shared memory protocol

The fleet keeps one persistent, shared memory so that knowledge compounds:
every agent starts already knowing the stack, conventions, and past findings
instead of rediscovering them. This is both a quality lever (agents act on
established facts) and the single biggest token saver (facts are derived once,
not once per agent per run).

## Location and layout

Everything lives in a `.fleet/` directory at the project root, **git-ignored**
(the coordinator adds `.fleet/` to `.gitignore` on first run if it isn't there).

```
.fleet/
├── memory.md            # the consolidated, always-current project knowledge base
├── docs/                # generated formal docs (PRD/BRD/FDD/TDD/ADR) — gitignored
└── log/
    └── <run-id>/
        ├── <agent>.md   # each agent's raw report for this run
        └── report.md    # the merged report for this run
```

`memory.md` is the durable brain. `log/` is the per-run history (useful for
diffing runs and debugging, safe to prune).

## The single-writer rule (why agents don't write memory directly)

Agents run in parallel. If several append to `memory.md` at once, the file
races and corrupts. So:

- **Agents read `memory.md`** at the start of their run (read-only).
- **Agents never write `memory.md`.** They end their report with a **Memory
  delta** — a short list of durable facts worth keeping.
- **The coordinator is the sole writer.** After each phase it collects the
  deltas, deduplicates them against what's already there, and writes the updated
  `memory.md`. Because only one process writes, there's no race.
- **Privacy gate before persisting.** Before writing a delta, scan it for
  secrets and PII (keys, tokens, emails, SSNs, customer data) and strip or
  redact them — memory records *where* a secret comes from (env, vault), never
  the value, and never personal data. Memory is a durable file every agent
  reads; it must not become a place sensitive data leaks into.

## Update cadence

Update memory **after every phase**, not just at the end — so agents in a later
phase (e.g. e2e after unit tests, or deploy after review) read the freshest
state. Concretely, the coordinator writes memory: after the review phase, after
applying fixes, after docs, and after deploy. Frequent small consolidations keep
memory current without ever risking a concurrent write.

## Keeping memory healthy

Memory is read by every agent on every run, so its size is a shared tax. Keep it
lean and true:

- **Record durable facts, not run output.** "The API uses Zod for request
  validation" belongs in memory; "test_login failed on 2026-07-04" belongs in
  the run report, not memory.
- **Deduplicate and supersede.** If a delta updates an existing fact (a command
  changed, a convention moved), replace the old line rather than appending a
  contradiction. When two facts conflict, the newer verified one wins — and note
  it, so agents don't re-flag the resolved question.
- **Prune stale entries.** If a fact no longer matches the code (verify before
  deleting), remove it. Stale memory is worse than no memory because agents
  trust it.

## memory.md template

The coordinator seeds this on first run and grows it over time. Keep sections;
keep entries terse.

```markdown
# Fleet Memory — <project name>
_Last updated: <date> by coordinator (run <run-id>)_

## Project overview
- What this project is, in 2-3 lines.

## Stack & commands (verified)
- Frontend: <framework> · test: `<cmd>` · lint: `<cmd>` · build: `<cmd>` · e2e: `<cmd>`
- Backend: <framework> · test: `<cmd>` · lint: `<cmd>` · e2e: `<cmd>`
- Package managers / lockfiles: <...>

## Testing harness (verified) — lets later runs skip rediscovery
- Server start command(s) + port(s) + readiness URL: <...>
- e2e/test runner location + invocation: <...>
- Browser/Playwright MCP available: <yes/no>
- Stable selectors for critical flows: <...>
- Design tokens / breakpoints (for the designer): <...>

## Architecture & conventions
- Directory layout, module boundaries, naming conventions.
- State management,