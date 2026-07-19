# ac-code-skill

**A fleet of seven principal-level engineering agents for your codebase — that verifies its own claims.**

`ac-code-skill` turns a broad *"test, clean up, document, and ship my code"* request into
seven specialist agents that each own one discipline, run in parallel, and merge into a
single prioritized report. It coordinates them through one shared memory plus living docs,
gates every state-changing step, and — the part that matters — **measures instead of
asserting**: contrast ratios are computed, font imports are probed, blocking findings need a
second agent's confirmation, and anything it can't verify is labelled unverified rather than
guessed.

Zero external dependencies. Every helper is standard-library Python; browser automation and
security scanning use MCP connectors or tools you already have, with graceful fallbacks.

---

## The seven agents

| Agent | Role | Owns |
|---|---|---|
| **Frontend** | UI Architect | rendering-paradigm fit, Core Web Vitals & perf budgets, WCAG 2.2/ARIA, design tokens, TS-at-scale, dead FE code/deps |
| **Backend** | Distributed Systems Architect | concurrency & back-pressure, distributed correctness (idempotency, CAP, consensus/CRDT), data architecture & query plans, API/event governance, migration safety |
| **Cyber Security** | AppSec Architect | logic flaws beyond scanners, crypto engineering, CI security gates, identity, supply chain (SBOM/SLSA), secrets, PII, advisory deps |
| **Tester** | Quality Architect (SDET) | all testing (unit/integration/e2e, both layers), suite strategy, flakiness root-causing, contract/perf/chaos, coverage, test authoring |
| **DevOps** | Platform Architect / SRE | self-service IDP, zero-downtime delivery (GitOps/canary), K8s/IaC, observability-as-code, deploy + auto-rollback, dep upgrades |
| **Docs** | Documentation Architect | PRD/BRD/FDD/TDD/ADR as **Word `.docx`** — auto-generated after review, auto-updated after fixes |
| **AI Agent Engineer** | Agentic Systems Architect | prompts & injection defence, agent/RAG architecture, evals, model choice, cost, guardrails — *dispatched only when the repo has AI features* |

Each reasons like a principal engineer: it catches the *class* of bug and the scaling cliff a
mid-level review misses, and frames fixes ADR-style with the trade-off (cost / risk / latency)
spelled out — while staying strictly in scope.

## How a run works

```
0. Memory      load shared state; agents RETRIEVE their slice (not the whole corpus)
1. Detect      stack, real commands, dependencies, AI signals — or greenfield → interview
2. Select      only the agents this repo and request actually need
3. Review      selected agents run in parallel, read-only → one merged report
4. Docs        .docx generated automatically, then the report is delivered
5. Fix         approved batches only → then docs regenerate
6. Deploy      health-checked, auto-rollback, destructive actions stop and ask
```

`run ac-code-skill` executes the whole pipeline, stopping only at the approval gates.

## What makes it different

- **It verifies instead of asserting.** Colour contrast is *computed*; font imports are
  *probed against the live provider*; a `blocking` finding requires a second agent to
  independently reproduce it. Anything unconfirmed ships labelled "unverified".
- **Retrieved memory, not bulk-loaded.** Memory and docs grow without bound. `recall.py`
  returns a pinned core plus task-matched sections — measured at **7% of a 219 KB corpus**
  on a real repo — and *lists what it omitted* so nothing is silently dropped.
- **An enforced privacy gate.** 18 typed PII categories × **BLOCK / REDACT / HASH / PASS**,
  applied before anything is persisted. `file:line` and public URLs are PASS-classed so
  findings stay reproducible; internal IPs are hashed so they stay correlatable without
  publishing your topology.
- **Living docs as Word files**, regenerated after fixes so they never drift from the code.
- **Self-improvement.** Agents feed an *Agent learnings* store; each run's refinements are
  inherited by that role on the next run.
- **Design system generation** from a plain-language brief — with a validation gate that
  refuses to ship an unreadable palette or a font it never imported.
- **Enhancements lane.** Forward-looking recommendations (impact × effort), kept separate
  from defect findings and tracked in a backlog so nothing is re-pitched.
- **Greenfield bootstrap.** An empty repo triggers a per-role intake interview, then docs
  and a scaffold.

## Install

**Claude Code (plugin marketplace)**
```
/plugin marketplace add arothm/CCSkill
/plugin install ac-code-skill@ccskill
```

**Or drop it in your skills folder**
```bash
git clone https://github.com/arothm/CCSkill.git
cp -r CCSkill/skills/ac-code-skill ~/.claude/skills/ac-code-skill
```

**Claude Desktop / Cowork** — upload the prebuilt `ac-code-skill.skill` under
**Settings → Capabilities → Skills**. Rebuild it after edits with:
```bash
cd CCSkill/skills && zip -r ../ac-code-skill.skill ac-code-skill
```

Then just ask:

> "Use ac-code-skill on this repo. Run the full review in parallel and give me one
> prioritized report. Don't change anything yet."

## The tooling

Every script is standard-library Python, runs offline, and is designed as a black box
(`--help`, then invoke).

```bash
# Compose a verified design system from a brief
python scripts/design_system.py "premium minimal SaaS landing page" --stack react
python scripts/design_system.py "<brief>" --persist -o .ac-code-skill   # MASTER.md + page overrides
python scripts/design_system.py --validate                  # 307 checks, non-zero exit on failure
python scripts/design_system.py --validate --check-fonts    # + probe providers for the families

# Retrieve the relevant slice of memory/docs instead of loading everything
python scripts/recall.py "budget race condition" --root .ac-code-skill --role backend

# Enforce the PII policy before anything is persisted
python scripts/redact.py --in report.md --strict
python scripts/redact.py --explain                          # the policy table

# Render docs to Word
python scripts/md_to_docx.py --in-dir src --out-dir .ac-code-skill/docs

# Testing/security helpers used by the agents
python scripts/with_server.py --help
python scripts/run_scanners.py --help
```

## Layout

```
skills/ac-code-skill/
├── SKILL.md                    # the coordinator: modes, phases, roster, gates
├── references/
│   ├── shared-rules.md         # the 5 rules every agent follows
│   ├── agent-roles.md          # each agent's principal-level brief
│   ├── memory.md               # shared-memory + docs protocol, privacy gate
│   ├── stack-detection.md      # language-agnostic stack/command/AI detection
│   ├── testing-harness.md      # zero-dep testing playbook
│   ├── design-inspiration.md   # aesthetic direction + IP guardrails
│   ├── report-format.md        # agent output + merged report shape
│   ├── deploy.md               # deploy runbook, rollback, gates
│   └── hooks.md                # optional continuous mode
├── data/                       # self-validating datasets
│   ├── styles.csv · palettes.csv · font-pairings.csv
│   ├── product-rules.csv · motion-libraries.csv
│   └── pii-policy.csv
└── scripts/                    # stdlib-only helpers
    ├── design_system.py · recall.py · redact.py
    └── md_to_docx.py · with_server.py · run_scanners.py
```

Runtime output lands in `.ac-code-skill/` in the target repo (git-ignored):
`memory.md`, `docs/*.docx`, `design-system/MASTER.md` + `pages/`, and `log/<run-id>/`
with each agent's raw report, evidence, and the merged report.

## Status & limitations

Stated plainly, because the skill itself forbids overclaiming:

- **The helper scripts are unit-verified, not integration-tested.** `--validate` (307
  checks), the live font probe, the redactor and the `.docx` renderer were each exercised
  against real data — but a full pipeline run *with all of this wired together* hasn't
  happened yet. The last end-to-end cycle predates several of these additions.
- **The design dataset is curated, not exhaustive** (13 styles / 14 palettes / 20 product
  types). Breadth was traded for correctness; the generator reports its own match confidence
  so a weak match is visible rather than silent.
- **`redact.py` catches pattern-detectable PII only.** Free-prose addresses, customer names
  and health data can't be regex-matched — the tool lists those categories every run so a
  human checks them deliberately.
- **The `.skill` bundle is committed and rebuilt by hand**, so it can drift from source
  until that's automated.
- **No test suite for the scripts themselves** — the one place the project doesn't yet meet
  the bar its own Tester agent sets.

## Licence

MIT.
