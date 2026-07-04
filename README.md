# CCSkill

A personal Claude skills marketplace. Currently ships one skill:

**`code-review-fleet`** — a coordinator skill that dispatches a fleet of
specialized review subagents (frontend & backend test / cleanup / e2e, frontend
designer, migration safety, security test / cleanup, docs, and VPS deploy) in
parallel over a codebase, coordinates them through one shared `.fleet/` memory,
and merges their findings into a single prioritized report. Fixes are
approval-gated; deploys run automatically with rollback behind safety gates.
Zero external dependencies (browser automation and security scanning use MCP
connectors or tools you already have, with graceful fallbacks).

---

## Install in Claude Code (plugin marketplace)

```
/plugin marketplace add arothm/CCSkill
/plugin install code-review-fleet@ccskill
```

Then just mention it, e.g.:

> "Use code-review-fleet on this repo. Run the full review in parallel, don't
> stop to confirm, and give me one prioritized report with actionable fixes.
> Don't change anything yet."

To update later: `/plugin marketplace update ccskill`.

Alternative (no marketplace) — clone the skill straight into your skills folder:

```bash
git clone https://github.com/arothm/CCSkill.git
cp -r CCSkill/skills/code-review-fleet ~/.claude/skills/code-review-fleet
```

## Install in Claude Desktop / Cowork

Skills upload as a `.skill` file (a zip of the skill folder). This repo ships a
prebuilt one:

1. Download **`code-review-fleet.skill`** from this repo.
2. In Claude Desktop, open **Settings → Capabilities → Skills** and upload it
   (requires a plan where custom skills are enabled).

To rebuild the `.skill` yourself after editing:

```bash
cd CCSkill/skills
zip -r ../code-review-fleet.skill code-review-fleet
```

---

## What's in the skill

```
skills/code-review-fleet/
├── SKILL.md                       # the coordinator: phases, roster, gates
├── references/
│   ├── shared-rules.md            # the 4 rules every agent follows
│   ├── memory.md                  # .fleet/ shared-memory protocol
│   ├── stack-detection.md         # language-agnostic stack/command detection
│   ├── agent-roles.md             # every agent's brief
│   ├── testing-harness.md         # zero-dep testing playbook (MCP browser, evidence)
│   ├── report-format.md           # agent output + merged report shape
│   └── deploy.md                  # auto-deploy runbook + rollback + gates
└── scripts/
    ├── with_server.py             # stdlib server-lifecycle helper (black box)
    └── run_scanners.py            # stdlib security-scanner runner (black box)
```

Runtime output in a target repo lives under `.fleet/` (gitignored): `memory.md`,
generated docs in `docs/`, and per-run logs/reports in `log/<run-id>/`.

## License

MIT (edit as you prefer).
