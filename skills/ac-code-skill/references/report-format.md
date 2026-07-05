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

Improvements:
- <optional: a refinement to how THIS agent should work next time — see
  shared-rules.md rule 5. The coordinator files these under Agent learnings.>
```

The **Memory delta** is how each agent feeds the shared memory without writing
it directly. The **Improvements** block is how each agent feeds the
self-improvement store. The coordinator collects both from all agents and
consolidates them into `.ac-code-skill/memory.md` (single writer — see
`memory.md`). Keep them durable and terse; per-run findings belong in the
report, not in memory.

## The merged report (you write this)

Save as `.ac-code-skill/log/<run-id>/report.md` (and show the summary inline to
the user). Use this template:

```markdown
# AC Code Skill — Review Report

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

## Dependency & dead-code health
- Outdated / EOL / advisory deps: <summary + which agent found them>
- Confirmed-unused deps / dead code / dead files / dead folders: <summary>

## Suggested fix batches
1. <batch the user can approve as a unit, e.g. "auto-formatting only">
2. <e.g. "the 3 null-check bugs">
3. <e.g. "the 2 security fixes — behavioral, confirm each">

## Docs
- Generated/updated at `.ac-code-skill/docs/`: <which docs>.
```

**Merge — don't staple.** Lead with the verdict and counts; group findings by
severity, *not* by agent; deduplicate shared root causes into one entry that
lists the agents that saw it; keep `file:line` + a concrete fix on every line.
The point of the fleet is one coherent report, not a pile of per-agent outputs.
