# Cortex

Autonomous brain and productivity OS for Claude Code.

## Quick Start

```bash
python ~/.claude/skills/cortex/bin/healthcheck.py
```

## Auto-Trigger Mechanism

Cortex uses a **one-layer** approach to guarantee it loads on every conversation:

1. **CLAUDE.md instruction** — `~/.claude/CLAUDE.md` tells Claude to invoke `/cortex` BEFORE responding to any first message

## CLAUDE.md Setup

Add this minimal block to `~/.claude/CLAUDE.md`:

````markdown
# STEP ZERO (every chat)
Skill(skill="cortex")

# First session each day
python ~/.claude/skills/cortex/bin/healthcheck.py

# Trigger `/cortex` from main conversation (not subagents)
````

## Naming Convention

| Folder | Pattern | Examples |
|--------|---------|---------|
| `docs/` | `{task-focused}.md` | `database-workflows`, `email-workflows` |
| `bin/` | `{action-noun}.py` | `healthcheck` |

## Docs

| Need | Go To |
|------|-------|
| Google Workspace commands | [docs/gws-quickref.md](docs/gws-quickref.md) |
| Create documents | [docs/create-documents.md](docs/create-documents.md) |
| Email workflows | [docs/email-workflows.md](docs/email-workflows.md) |
| Media processing | [docs/media-processing.md](docs/media-processing.md) |
| Database workflows | [docs/database-workflows.md](docs/database-workflows.md) |
| Data pipelines | [docs/data-pipelines.md](docs/data-pipelines.md) |
| Setup/troubleshooting | [docs/setup.md](docs/setup.md) |
