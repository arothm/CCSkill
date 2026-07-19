# Continuous mode — recommended Claude Code hooks

The fleet is normally *invoked*: you ask, it runs. Hooks make parts of it
*continuous* — memory is primed automatically, edits are checked as they happen,
and a commit carrying a secret is stopped before it lands.

**This file is a recommendation, not an installer.** Hooks execute commands on
your machine with your permissions, so the coordinator must **never write them
into your settings unsilently** — show the config, explain what each hook costs,
and let the user install it (the `update-config` skill does this cleanly, or
edit `.claude/settings.json` by hand).

## The three that earn their keep

Set `SKILL` to wherever the skill lives (e.g. `~/.claude/skills/ac-code-skill`).

```jsonc
{
  "hooks": {
    // 1. Prime the session with RELEVANT memory instead of bulk-loading it.
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$SKILL/scripts/recall.py\" \"session start: current branch work\" --root .ac-code-skill --top 4 || true",
            "timeout": 15
          }
        ]
      }
    ],

    // 2. Refuse to commit a secret. Blocking is the point here.
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "git diff --cached 2>/dev/null | python \"$SKILL/scripts/redact.py\" --strict >/dev/null",
            "timeout": 20
          }
        ]
      }
    ],

    // 3. Fast feedback on what was just edited (keep it FAST - it runs constantly).
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npm run -s typecheck --if-present || true",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

## What each one buys you

| Hook | Effect | Why it's worth it |
|---|---|---|
| `SessionStart` → `recall.py` | the session opens already knowing the relevant memory | replaces "every agent reads all of memory" with "the session gets the ~5% that matters" |
| `PreToolUse` (Bash) → `redact.py --strict` | non-zero exit blocks the commit when a BLOCK-class value is staged | the one place a hard block is justified — a leaked credential is not recoverable by editing history later |
| `PostToolUse` (Edit\|Write) → typecheck | catches a break at the moment it's introduced | a type error found now costs seconds; found in the review phase it costs a whole cycle |

## Rules for adding your own

- **Fast or nothing.** `PostToolUse` fires on every edit. Anything over a couple
  of seconds turns the session sluggish; put slow work (full suite, scanners) in
  the review phase where it belongs, not a hook.
- **Only block on the irreversible.** Use a non-zero exit to *stop* an action
  only where the damage can't be undone — a committed secret. Everything else
  should warn (`|| true`) and let the human decide.
- **Never silently mutate.** A hook that rewrites files under the user is
  indistinguishable from a bug. Check and report; leave the fix to the fix phase.
- **Assume it runs without a repo.** Guard with `--if-present`, `|| true`, and
  tolerate a missing `.ac-code-skill/` — a hook that errors on a fresh clone
  trains people to delete hooks.
- **Cost is real.** Every hook runs on every matching event forever. Add one only
  if you can say what it saves.
