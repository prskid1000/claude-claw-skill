# Cortex

Autonomous brain, project tracker, and productivity OS for Claude Code.

## What It Does

Cortex is an always-on skill that gives Claude Code persistent memory, Jira-like project tracking, and deep tool orchestration — all powered by Obsidian, Google Workspace, and local Python tooling.

| Capability | How |
|------------|-----|
| **Persistent Knowledge** | Obsidian vault with structured KB mesh, auto-synced via background subagents |
| **Issue Tracking** | Epics / Stories / Tasks / Bugs with status workflows, sprints, kanban board |
| **Document Creation** | Excel, Word, PowerPoint, PDF — styled, with charts, uploaded to Drive |
| **Email Automation** | Compose with MIME, attach generated docs, send via Gmail CLI |
| **Database Queries** | MySQL MCP for schema exploration, analytics, data export |
| **Media Processing** | FFmpeg (audio/video), Pillow (images), ImageMagick, Pandoc |
| **Data Pipelines** | CSV→Excel→Sheets, DB→Report→Email, PDF extraction, format conversion |
| **Adaptive Sync** | Dynamic cron heartbeats that scale with work intensity |
| **Self-Healing** | Auto-test environment, auto-install missing packages, auto-improve docs |

## Structure

```
cortex/
├── SKILL.md              # Entry point — file map, heartbeat lifecycle, triggers
├── README.md             # This file
├── docs/                 # Reference documentation (9 files)
│   ├── knowledge-base    # Obsidian KB system + 14 MCP tools
│   ├── issue-tracker     # Jira-like board + ticket templates
│   ├── workspace         # Google Workspace CLI (Drive/Sheets/Docs/Slides/Gmail/Calendar)
│   ├── doc-forge         # Document creation recipes (Excel/Word/PPT/PDF)
│   ├── mailbox           # Email composition + Gmail workflows
│   ├── media-kit         # FFmpeg / Pillow / ImageMagick / Pandoc / screenshots
│   ├── datastore         # MySQL MCP queries + export patterns
│   ├── pipelines         # End-to-end data conversion flows
│   └── bootstrap         # Setup, install, and troubleshooting guide
├── bin/                  # Utility scripts (3 files)
│   ├── healthcheck.py    # Verify all 29 dependencies
│   ├── evolve.py         # Self-improvement analysis
│   └── stash.py          # Capture reusable scripts to cookbook/
└── cookbook/              # Auto-populated reusable script templates
```

## Auto-Trigger Mechanism

Cortex uses a **three-layer** approach to guarantee it loads on every conversation:

1. **CLAUDE.md instruction** — `~/.claude/CLAUDE.md` tells Claude to invoke `/cortex` BEFORE responding to any first message
2. **Skill description** — leads with `ALWAYS LOAD THIS SKILL ON EVERY CONVERSATION WITHOUT EXCEPTION` plus `priority: critical`
3. **Skill-level hooks** (in SKILL.md frontmatter) — `UserPromptSubmit` reminder, `PreCompact` flush warning, `Stop` cleanup

### Lifecycle

- **Session start** — CLAUDE.md + skill description trigger cortex; reads KB, runs healthcheck
- **During work** — KB syncs inline on event triggers (subtask done, error, decision, etc.)
- **Pre-compact** — hook reminds Claude to flush all pending KB entries, Board snapshot, WorkLog
- **Session end** — hook cleans up temp marker files

## Obsidian KB Structure

Cortex expects (and will create on first run) this vault structure:

```
Vault/
├── KB/
│   ├── _index.md                # Root index → links to all branches
│   ├── Projects/{Name}/
│   │   ├── _index.md            # Project overview
│   │   ├── Architecture.md      # System design, tech stack
│   │   ├── Entities.md          # Domain models, schemas
│   │   ├── Patterns.md          # Conventions & patterns
│   │   ├── APIs.md              # Endpoints, services
│   │   ├── Bugs.md              # Known issues, gotchas
│   │   └── {Topic}.md           # Other dense topic nodes
│   ├── Patterns/                # Cross-project patterns
│   ├── Decisions/               # ADR-style: {YYYY-MM-DD}-{slug}.md
│   └── People/                  # Team roles, preferences
├── Board/
│   ├── _board.md                # Kanban dashboard
│   ├── _counter.md              # Auto-increment ticket IDs
│   ├── Epics/                   # EPIC-NNN.md
│   ├── Stories/                 # STORY-NNN.md
│   ├── Tasks/                   # TASK-NNN.md
│   └── Bugs/                    # BUG-NNN.md
├── WorkLog/{YYYY-MM}.md         # Append-only monthly log
└── Research/                    # Deep-dive notes
```

## CLAUDE.md Setup

Copy the block below into your `~/.claude/CLAUDE.md` to enable automatic cortex bootstrap. This is the most critical piece — without it, Claude may not invoke the skill on session start.

````markdown
# User-Level Instructions

---

## ⚠️ STEP ZERO — DO THIS FIRST, EVERY TIME ⚠️

**Your VERY FIRST action in EVERY conversation MUST be:**

```
Skill(skill="cortex")
```

- Do NOT output ANY text before invoking `/cortex`
- Do NOT greet the user first
- Do NOT acknowledge the user's message first
- Do NOT reason about whether cortex is needed — it ALWAYS is
- The skill call must be the FIRST tool call in your FIRST response, before anything else
- If the `UserPromptSubmit` hook fires "CORTEX BOOTSTRAP REQUIRED" and you have NOT yet invoked `/cortex`, you have already failed — invoke it IMMEDIATELY

**After `/cortex` loads**, execute the bootstrap sequence it describes (read KB, run healthcheck if first session today), THEN respond to the user.

---

## Cortex Script Triggers (MANDATORY)

These scripts live in `~/.claude/skills/cortex/bin/`. Run them at the specified times — no exceptions.

### `healthcheck.py` — First session of the day
- Run `python ~/.claude/skills/cortex/bin/healthcheck.py` during bootstrap if it hasn't been run today
- If any check fails, attempt auto-fix or warn the user
- Do NOT skip this — environment drift causes silent failures

### `evolve.py` — Every completed subtask
- After completing every subtask, run:
  `python ~/.claude/skills/cortex/bin/evolve.py`
- If `--apply` would fix issues, ask the user before applying
- Log improvements in WorkLog

### `stash.py` — After creating any reusable script
- When you write a Python script during a session that could be reused (data pipeline, report generator, converter, etc.), capture it:
  `python ~/.claude/skills/cortex/bin/stash.py --name "descriptive-name" --source /path/to/script.py --tags "tag1,tag2"`
- Signs of a reusable script: generic logic, no hardcoded project values, solves a common task
- Do NOT stash one-off debugging scripts or project-specific glue code

---

## Re-invoke Cortex

Re-invoke `/cortex` when the user mentions: obsidian, KB, knowledge, worklog, board, epic, story, sprint, ticket, issue, google workspace, gws, drive, sheets, docs, slides, gmail, calendar, email, pdf, excel, word, powerpoint, screenshot, ffmpeg, pandoc, imagemagick, document, report, invoice, presentation, spreadsheet, chart, image, video, audio, convert, export, database, mysql, query, sql.

## Pre-Compact Protocol (CRITICAL — before context compaction)

Before context window compaction occurs:
1. Spawn KB subagent: flush ALL pending WorkLog entries
2. Patch all KB nodes touched this session
3. Board snapshot: update all IN_PROGRESS tickets
4. Write resume note: `KB/Projects/{name}/Resume.md`

## Important: Hook Subagents Cannot Load Skills

Agent-type hooks in settings.json spawn subagents that have NO access to skills. Do not rely on hooks to run `/cortex` bootstrap — it must be triggered from the main conversation via the skill system.
````

## Naming Convention

| Folder | Pattern | Examples |
|--------|---------|---------|
| `docs/` | `{domain-noun}.md` | `knowledge-base`, `datastore`, `mailbox` |
| `bin/` | `{action-noun}.py` | `healthcheck`, `evolve`, `stash` |
| `cookbook/` | `{descriptive-name}.py` | `csv-to-styled-excel`, `pdf-invoice-parser` |

## Quick Start

```bash
# Verify environment
python ~/.claude/skills/cortex/bin/healthcheck.py

# Check skill quality
python ~/.claude/skills/cortex/bin/evolve.py

# Capture a useful script
python ~/.claude/skills/cortex/bin/stash.py --name "my-script" --source /tmp/script.py --tags "excel,report"
```

## Requirements

| Category | Tools |
|----------|-------|
| **Python packages** | openpyxl, python-docx, python-pptx, pymupdf, PyPDF2, reportlab, pdfplumber, pillow, lxml, beautifulsoup4 |
| **CLI tools** | gws, git, ffmpeg, pandoc, imagemagick |
| **MCP servers** | obsidian, mysql (optional), chrome-devtools (optional), clickup (optional) |

See [docs/bootstrap.md](docs/bootstrap.md) for installation instructions.

## How It Works

1. **Session start** — reads Obsidian KB + WorkLog + Board for context, cleans orphan crons, sets adaptive heartbeat
2. **During work** — tracks knowledge via background subagents, manages tickets, adjusts sync interval
3. **On events** — errors create BUG tickets, completions close TASKs, decisions get logged
4. **Session end** — flushes all pending knowledge, tears down crons, no orphans
