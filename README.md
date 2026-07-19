# CCSkill

A personal Claude skills marketplace. Currently ships one skill:

## `ac-code-skill`

A coordinator skill that dispatches a fleet of **seven principal/staff-level
role-agents** in parallel over a codebase, coordinates them through one shared
`.ac-code-skill/` memory plus living docs, and merges their findings into a
single prioritized report. Each agent reasons like a principal engineer for its
discipline — it catches the class of bug and scaling cliff a mid-level review
misses, and proposes fixes with the trade-off (cost/risk/latency) spelled out —
while staying strictly in scope and verifying every claim against real command
output.

### The seven agents

| Agent | Role | Owns |
|---|---|---|
| **Frontend** | UI Architect | rendering paradigm fit, Core Web Vitals & perf budgets, WCAG 2.2/ARIA, design tokens, TS-at-scale, dead FE code/deps |
| **Backend** | Distributed Systems Architect | concurrency/back-pressure, distributed correctness (idempotency, CAP, consensus/CRDT), data architecture & query plans, API/event governance, migration safety, dead BE code/deps |
| **Cyber Security** | AppSec Architect (builder) | logic-flaw analysis beyond scanners, crypto engineering, CI security gates, identity, supply chain (SBOM/SLSA), secrets, PII, outdated/advisory deps |
| **Tester** | Quality Architect (SDET) | all testing (unit/integration/e2e, both layers), strategy, flakiness, contract/perf/chaos, coverage, quality dashboards, test authoring |
| **DevOps** | Platform Architect / SRE | self-service IDP, zero-downtime delivery (GitOps/canary), K8s/IaC, observability-as-code, deploy + auto-rollback, server patches, dep upgrades |
| **Docs** | Documentation Architect | PRD/BRD/FDD/TDD/ADR as **Word `.docx`** — auto-generated after review, auto-updated after fixes |
| **AI Agent Engineer** | Agentic Systems Architect | AI/LLM features: prompts & injection defense, agent/RAG architecture, evals, model choice, cost, guardrails (dispatched only when the repo has AI) |

### How it works

1. **Memory & docs** — load or bootstrap the shared `.ac-code-skill/` state.
2. **Detect** the stack, commands, dependencies, and AI signals — or, on an empty
   repo, switch to **greenfield mode** and interview you from every agent's
   perspective before scaffolding.
3. **Select & confirm** which agents the repo and request actually need.
4. **Review** — the selected agents run in parallel, read-only, and their
   findings merge into one prioritized report.
5. **Docs** — documentation is generated automatically, then the report is
   delivered.
6. **Fix** — approved fixes only, applied in batches; docs auto-update afterward.
7. **Deploy** — automatic, with health checks and rollback behind safety gates.

### What makes it different

- **One-prompt full run** — `run ac-code-skill` executes the whole pipeline end
  to end, stopping only at the approval gates for fixes and deploys.
- **Living docs as Word files** — PRD/BRD/FDD/TDD/ADR generated as `.docx` after
  review and refreshed again after fixes, so the documentation always matches the
  code.
- **Shared memory + self-improvement** — every agent reads the full memory and
  docs each run and feeds an *Agent learnings* store, so the fleet compounds
  skill over time, not just knowledge.
- **Dependency & dead-code hygiene** — outdated/EOL/advisory packages, unused
  dependencies, and dead code/files/folders are swept every run.
- **Greenfield bootstrap** — an empty repo triggers a per-role intake interview
  that turns your answers into docs and a scaffold.
- **Design system generation** — `design_system.py "premium minimal SaaS landing
  page"` composes a concrete spec from bundled datasets: layout pattern, style,
  colour tokens as CSS variables with a **measured** WCAG ratio on every pair,
  typography with the correct provider import, anti-patterns, and a checklist.
  Persists as `design-system/MASTER.md` plus per-page overrides. `--validate`
  gates the dataset itself — contrast, font-import coherence, referential
  integrity — so it can't ship an unreadable palette or a font it never imported.
- **Aesthetic direction** — an adjective brief ("premium minimal", "editorial")
  is translated into concrete design vocabulary and calibrated against catalogued
  reference libraries (composition, components, motion, WebGL), then implemented
  originally in your own tokens and stack — principles learned, never cloned, with
  performance and accessibility budgets still binding.
- **Zero external dependencies** — browser automation and security scanning use
  MCP connectors or tools you already have, with graceful fallbacks.

---

## Install in Claude Code (plugin marketplace)

```
/plugin marketplace add arothm/CCSkill
/plugin install ac-code-skill@ccskill
```

Then just mention it, e.g.:

> "Use ac-code-skill on this repo. Run the full review in parallel, don't
> stop to confirm, and give me one prioritized report with actionable fixes.
> Don't change anything yet."

To update later: `/plugin marketplace update ccskill`.

Alternative (no marketplace) — clone the skill straight into your skills folder:

```bash
git clone https://github.com/arothm/CCSkill.git
cp -r CCSkill/skills/ac-code-skill ~/.claude/skills/ac-code-skill
```

## Install in Claude Desktop / Cowork

Skills upload as a `.skill` file (a zip of the skill folder). This repo ships a
prebuilt one:

1. Download **`ac-code-skill.skill`** from this repo.
2. In Claude Desktop, open **Settings → Capabilities → Skills** and upload it
   (requires a plan where custom skills are enabled).

To rebuild the `.skill` yourself after editing:

```bash
cd CCSkill/skills
zip -r ../ac-code-skill.skill ac-code-skill
```

---

## What's in the skill

```
skills/ac-code-skill/
├── SKILL.md                       # the coordinator: modes, phases, roster, gates
├── references/
│   ├── shared-rules.md            # the 5 rules every agent follows
│   ├── memory.md                  # .ac-code-skill/ shared-memory + docs protocol
│   ├── stack-detection.md         # language-agnostic stack/command/AI detection
│   ├── agent-roles.md             # every agent's principal-level brief
│   ├── design-inspiration.md      # aesthetic direction: reference libraries + IP guardrails
│   ├── testing-harness.md         # zero-dep testing playbook (MCP browser, evidence)
│   ├── report-format.md           # agent output + merged report shape
│   └── deploy.md                  # auto-deploy runbook + rollback + gates
├── data/                          # verified design datasets (self-validating)
│   ├── styles.csv                 #   13 styles: best-for, avoid-for, effects, a11y risk
│   ├── palettes.csv               #   14 palettes, every token pair contrast-checked
│   ├── font-pairings.csv          #   13 pairings w/ provider + matching import URL
│   └── product-rules.csv          #   20 product types → pattern, style, anti-patterns
└── scripts/
    ├── with_server.py             # stdlib server-lifecycle helper (black box)
    ├── run_scanners.py            # stdlib security-scanner runner (black box)
    ├── md_to_docx.py              # stdlib Markdown→Word (.docx) renderer (black box)
    └── design_system.py           # stdlib design-system composer + --validate gate
```

Runtime output in a target repo lives under `.ac-code-skill/` (gitignored):
`memory.md`, docs auto-generated into `docs/` as **Word `.docx`** files (refreshed
after review and again after fixes), and per-run logs/reports in `log/<run-id>/`.

## License

MIT (edit as you prefer).
