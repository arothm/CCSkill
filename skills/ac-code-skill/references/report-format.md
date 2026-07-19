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

Findings:   # defects only — something is wrong
- [blocking] path/to/file.ts:42 — <problem>. Fix: <concrete suggestion>.
- [warning]  path/to/other.py:88 — <problem>. Fix: <concrete suggestion>.
- [nit]      path/to/thing.jsx:12 — <problem>. Fix: <concrete suggestion>.

Enhancements:   # optional, ≤3 — nothing is broken, but here's a better way
- [impact:H effort:S] path/or/area — <enhancement>. Why: <concrete benefit>.
- [impact:M effort:M] path/or/area — <enhancement>. Why: <concrete benefit>.

Memory delta:
- <durable fact worth persisting — a convention, a working command, a recurring
  issue class. Omit transient run output. Empty is fine if nothing new.>

Improvements:
- <optional: a refinement to how THIS agent should work next time — see
  shared-rules.md rule 5. The coordinator files these under Agent learnings.>
```

**Findings vs Enhancements** are two different things: a *finding* is a defect
(something is wrong, severity-graded), an *enhancement* is a forward-looking
improvement (nothing is wrong, but here's a better way) — capped at 3 per agent,
tagged impact × effort, and kept out of the severity counts. The **Memory delta**
is how each agent feeds the shared memory without writing it directly; the
**Improvements** block feeds the self-improvement store. The coordinator collects
all of these, folds enhancements into the report's *Recommendations* section (and
the memory enhancement backlog), and consolidates deltas + improvements into
`.ac-code-skill/memory.md` (single writer — see `memory.md`). Keep them durable
and terse; per-run findings belong in the report, not in memory.

## The merged report (you write this)

Save as `.ac-code-skill/log/<run-id>/report.md` (and show the summary inline to
the user). Use this template:

```markdown
# AC Code Skill — Review Report

**Verdict:** <PASS / NEEDS WORK / BLOCKED>
**Counts:** N blocking · M warnings · K nits
**Scope:** <diff vs main | full repo> · **Agents:** <which ran>

## Blocking
_Every entry here was independently confirmed by a second agent (shared-rules
rule 1). Anything one agent found but another couldn't reproduce belongs in
Warnings, labelled "single-agent, unconfirmed"._
- **<short title>** — `file:line` (from: <agent>, confirmed by: <second agent>)
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

## Recommendations & enhancements   (forward-looking — NOT defects)
_Nothing below is broken; these are where investment would pay off. Ranked by
rough ROI (impact ÷ effort). Advisory — implementing one is approval-gated._
- **[impact:H · effort:S]** <area> — <enhancement>. Why: <concrete benefit>. (from: <agent>)
- **[impact:M · effort:M]** <area> — <enhancement>. Why: <concrete benefit>. (from: <agent>)
- <omit this whole section on a quick diff-check; include it on a full run / cycle>

## Docs
- Generated/updated as Word `.docx` at `.ac-code-skill/docs/`: <which docs>.
```

**Merge — don't staple.** Lead with the verdict and counts; group findings by
severity, *not* by agent; deduplicate shared root causes into one entry that
lists the agents that saw it; keep `file:line` + a concrete fix on every line.
The point of the fleet is one coherent report, not a pile of per-agent outputs.

**Run the report through the privacy gate before saving it.** `python
scripts/redact.py --in report.md --strict` — a review artefact is a durable file
that gets shared, and it is exactly where a leaked credential or a real person's
address should not end up (see `memory.md`). Keep `file:line` paths and public
URLs; they're PASS-classed so findings stay reproducible.

**Keep enhancements out of the defect counts.** The verdict and blocking/warning/
nit counts are about *defects only* — an enhancement is never a `blocking`. Rank
the Recommendations by impact ÷ effort, dedupe against the memory enhancement
backlog (don't re-list something already done or declined), and cap the whole
section to the strongest ~8 so it stays a shortlist, not a wishlist.
