# Report format

Two uses: (1) the shape each agent returns, and (2) the merged report you write.

## Severity levels

- **blocking** — must fix before merge: failing test, build break, security
  hole, a real bug.
- **warning** — should fix: risky pattern, missing error handling, meaningful
  code smell, missing coverage on changed logic.
- **nit** — optional polish: formatting, naming, minor duplication.

## What each agent returns

```
Summary: <one paragraph — did tests pass? overall health of this lane?>

Findings:
- [blocking] path/to/file.ts:42 — <problem>. Fix: <concrete suggestion>.
- [warning]  path/to/other.py:88 — <problem>. Fix: <concrete suggestion>.
- [nit]      path/to/thing.jsx:12 — <problem>. Fix: <concrete suggestion>.

Memory delta:
- <durable fact worth persisting — a convention, a working command, a recurring
  issue class. Omit transient run output. Empty is fine if nothing new.>
```

The **Memory delta** is how each agent feeds the shared memory without writing
it directly. The coordinator collects deltas from all agents and consolidates
them into `.fleet/memory.md` (single writer — see `memory.md`). Keep deltas
durable and terse; per-run findings belong in the report, not in memory.

## The merged report (you write this)

Save as `code-review-report.md` in the working directory. Use this template:

```markdown
# Code Review Fleet — Report

**Verdict:** <PASS / NEEDS WORK / BLOCKED>
**Counts:** N blocking · M warnings · K nits
**Scope:** <diff vs main | full repo> · **Agents:** <which ran>

## Blocking
- **<short title>** — `file:line` (from: <agent>)
  <problem>. **Fix:** <suggestion>.

## Warnings
- **<short title>** — `file:line` (from: <agent>)
  <problem>. **Fix:** <suggestion>.

## Nits
- `file:line` — <problem>. Fix: <suggestion>.

## Test & tooling results
- frontend tests: <pass/fail + summary>
- backend tests: <pass/fail + summary>
- linters/type-checkers: <summary>

## Suggested fix batches
1. <batch the user can approve as a unit, e.g. "auto-form