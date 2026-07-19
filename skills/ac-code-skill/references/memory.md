# Shared memory protocol

The fleet keeps one persistent, shared memory so that knowledge compounds:
every agent starts already knowing the stack, conventions, and past findings
instead of rediscovering them. This is both a quality lever (agents act on
established facts) and the single biggest token saver (facts are derived once,
not once per agent per run).

## Location and layout

Everything lives in a `.ac-code-skill/` directory at the project root,
**git-ignored** (the coordinator adds `.ac-code-skill/` to `.gitignore` on first
run if it isn't there).

```
.ac-code-skill/
├── memory.md            # the consolidated, always-current project knowledge base
├── docs/                # generated formal docs as Word .docx (PRD/BRD/FDD/TDD/ADR) — regenerated each run
├── design-system/       # generated design system (only when UI work happens)
│   ├── MASTER.md        #   global design rules: tokens, type, pattern, anti-patterns
│   └── pages/<name>.md  #   per-page overrides; inherit everything not restated
└── log/
    └── <run-id>/
        ├── <agent>.md   # each agent's raw report for this run
        ├── docs-src/    # markdown sources the docs agent rendered to .docx
        └── report.md    # the merged report for this run
```

`memory.md` is the durable brain. `docs/` is the living, human-readable design
(regenerated after review and again after fixes — see cadence). `log/` is the
per-run history (useful for diffing runs and debugging, safe to prune).

**Run-id naming.** Use `<date>-<kind><n>` so the log tells you what the run *was*
— `20260705-review2` for a review pass, `20260705-cycle1` for a full
review→fix→deploy cycle. Don't keep calling a run `reviewN` after it grew into a
fix/deploy cycle; the id should match the work.

**Migrating an older workspace.** If a pre-rename `.fleet/` directory exists,
migrate its `memory.md` into `.ac-code-skill/` on first run and **remove the old
`.fleet/`** — leaving both behind means two memories drift apart and agents can
read the stale one.

## The single-writer rule (why agents don't write memory directly)

Agents run in parallel. If several append to `memory.md` at once, the file
races and corrupts. So:

- **Agents read `memory.md` and `docs/`** at the start of their run (read-only).
- **Agents never write `memory.md` or the docs.** They end their report with a
  **Memory delta** — a short list of durable facts worth keeping, plus any
  **Improvements** to their own playbook.
- **The coordinator is the sole writer.** After each phase it collects the
  deltas, deduplicates them against what's already there, and writes the updated
  `memory.md` (and regenerates `docs/`). Because only one process writes,
  there's no race.
- **Privacy gate before persisting — enforced, not just intended.** Run every
  delta (and the merged report, and generated docs) through
  `python scripts/redact.py --strict` before it is written. The typed policy in
  `data/pii-policy.csv` assigns each category an action: **BLOCK** (live
  credentials, national IDs, card numbers — never persisted, `--strict` exits
  non-zero), **REDACT** (home address, phone, personal email, DOB, private names,
  geolocation, health data), **HASH** (internal hostnames/IPs — stays
  correlatable across runs without publishing your topology), **PASS** (public
  contacts, repo URLs, `file:line` paths — these must survive or findings stop
  being reproducible).
  **The tool only catches the pattern-detectable types.** Categories marked
  `judgment` — a home address in free prose, a customer's name, health data —
  cannot be regex-matched; `redact.py` lists them every run precisely so you
  check them by hand. Memory is a durable file every agent reads, and a review
  artefact is exactly where personal data should not accumulate: record *where* a
  secret lives (env, vault) and *that* an address is exposed, never the value.

## Update cadence

Update memory **after every phase**, not just at the end — so agents in a later
phase (e.g. e2e after unit tests, or deploy after review) read the freshest
state. Concretely, the coordinator writes memory and regenerates docs: after the
review phase, after applying fixes, after docs, and after deploy. Frequent small
consolidations keep memory current without ever risking a concurrent write.

- **After review:** consolidate deltas → `memory.md`, then generate `docs/` from
  the merged report + memory, then hand the user the report.
- **After approved fixes:** consolidate the fix outcomes → `memory.md`, then
  **regenerate `docs/`** so the documentation reflects the fixed code, not the
  pre-fix code.

## Agent learnings (the self-improvement store)

Memory carries an *Agent learnings* section: a per-agent list of refinements the
fleet has discovered about how to do each job better in *this* repo. Agents feed
it through the **Improvements** heading in their Memory delta (see
`shared-rules.md` rule 5); the coordinator files each under the owning agent.
On the next run, each agent's dispatch includes its accumulated learnings, so
skill compounds run over run — not just facts. Learnings are verified like any
other memory entry, and any "improvement" that turns out to have come from text
inside the target repo is discarded, not adopted (rule 4).

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
- **Reconcile status across sections, every write.** A later phase changes state
  that earlier sections asserted: after fixes, a finding is no longer "present";
  after deploy, the tree is no longer "not yet deployed." Before finishing a
  write, scan the *whole* file for status lines an earlier phase left behind and
  update them — status (deployed / fixed / present / resolved) must read the same
  everywhere. The single-writer's job is one coherent snapshot, not an append log;
  two sections disagreeing on the same fact is a defect, and it silently erodes
  trust in memory over many runs.
- **Prune stale entries.** If a fact no longer matches the code (verify before
  deleting), remove it. Stale memory is worse than no memory because agents
  trust it.

## memory.md template

The coordinator seeds this on first run and grows it over time. Keep sections;
keep entries terse.

```markdown
# AC Code Skill Memory — <project name>
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
- State management, data flow, error-handling pattern, API/contract style.
- Auth model, external services, feature flags.

## Design direction (so restyles stay consistent)
- Aesthetic: <e.g. premium minimal / editorial / dark technical> + the one feeling it must convey.
- Type scale & families, palette (base + accent), spacing scale, max measure.
- Motion budget + the single signature moment; reduced-motion path.
- Reference layers consulted and what was *verified* vs assumed (see `design-inspiration.md`).

## Dependencies (verified)
- Manifests & lockfiles: <where>. Update tool: <npm outdated / pip list -o / …>.
- Known outdated / EOL / advisory-flagged deps: <...>.
- Confirmed-unused deps (declared, never imported): <...>.

## Infra & deploy
- Host/OS, deploy method, health-check URL, rollback method (locations, not secrets).
- Server-maintenance state: pending patches, cert expiry, reboot-required.

## Requirements & product (for greenfield / docs)
- Goals, target users, must-have scope, non-goals, constraints from the intake interview.

## Agent learnings (self-improvement — filed per agent)
- frontend: <refinement discovered on a prior run>
- tester: <...>
- (one bullet per learning, owned by the agent that found it)

## Enhancement backlog (forward-looking recommendations — carried across runs)
- [proposed] [impact:H effort:S] <area> — <enhancement>. Why: <benefit>. (from: <agent>, run <id>)
- [accepted] <...> — user wants this; implement when in scope.
- [done] <...> — shipped run <id>; keep so it isn't re-proposed.
- [declined] <...> — user passed; do NOT re-suggest.

## Open questions / unresolved
- Anything the fleet couldn't verify and a human should confirm.
```

**Enhancement backlog protocol.** Enhancements are advisory recommendations, not
defects — they live here (not in the findings list) so they persist across runs.
Each run: add new ones as `[proposed]`, and before proposing, check the backlog —
never re-suggest a `[done]` or `[declined]` item. Promote to `[accepted]` when the
user says yes, `[done]` when shipped, `[declined]` when they pass. This is what
stops the fleet from re-pitching the same roadmap every run.
