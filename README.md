# CCSkill

A personal Claude skills marketplace. Currently ships one skill:

**`ac-code-skill`** — a coordinator skill that dispatches a fleet of seven
role-shaped subagents (**Frontend**, **Backend**, **Cyber Security**,
**Tester**, **DevOps**, **Docs**, and an **AI Agent Engineer** for repos with
AI/LLM features) in parallel over a codebase, coordinates them through one
shared `.ac-code-skill/` memory plus living docs, and merges their findings into
a single prioritized report. Every agent reads the full current memory and docs each run, checks for
outdated and dead/unused dependencies and dead code/files/folders, and improves
its own playbook as it works. Docs are generated automatically after review and
updated automatically after approved fixes; fixes are approval-gated; deploys
run automatically with rollback behind safety gates. `run ac-code-skill` runs
the whole pipeline in one prompt, and on an empty repo the skill interviews you
from every agent's perspective to bootstrap a new project from scratch. Zero
external dependencies (browser automation and security scanning use MCP
connectors or tools you already have, with graceful fallbacks).

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
├── SKILL.md                       # the coordinator: phases, roster, gates
├── references/
│   ├── shared-rules.md            # the 5 rules every agent follows
│   ├── memory.md                  # .ac-code-skill/ shared-memory + docs protocol
│   ├── stack-detection.md         # language-agnostic stack/command detection
│   ├── agent-roles.md             # every agent's brief
│   ├── testing-harness.md         # zero-dep testing playbook (MCP browser, evidence)
│   ├── report-format.md           # agent output + merged report shape
│   └── deploy.md                  # auto-deploy runbook + rollback + gates
└── scripts/
    ├── with_server.py             # stdlib server-lifecycle helper (black box)
    └── run_scanners.py            # stdlib security-scanner runner (black box)
```

Runtime output in a target repo lives under `.ac-code-skill/` (gitignored):
`memory.md`, docs auto-generated into `docs/` (refreshed after review and again
after fixes), and per-run logs/reports in `log/<run-id>/`.

## License

MIT (edit as you prefer).
