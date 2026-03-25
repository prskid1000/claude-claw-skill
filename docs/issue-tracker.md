# Issue Tracker — Jira-like Board

> Epics, stories, tasks, bugs with status workflows, sprints, and kanban dashboard in Obsidian.

**Related:** [knowledge-base.md](knowledge-base.md) | [workspace.md](workspace.md)

---

## Hierarchy

```
Epic (EPIC-NNN)         ← large initiative
 └── Story (STORY-NNN)  ← deliverable feature
      └── Task (TASK-NNN) ← atomic work item
Bug (BUG-NNN)           ← standalone, linked to story/epic if relevant
```

## Status Workflows

**Standard:** `BACKLOG → TODO → IN_PROGRESS → IN_REVIEW → DONE` (+ `BLOCKED` with reason)

**Bugs:** `OPEN → INVESTIGATING → ROOT_CAUSED → FIXING → VERIFIED → CLOSED`

## Vault Structure

```
Board/
├── _board.md            # Kanban dashboard (aggregated view)
├── _counter.md          # Next IDs: {epic: N, story: N, task: N, bug: N}
├── Epics/EPIC-{NNN}.md
├── Stories/STORY-{NNN}.md
├── Tasks/TASK-{NNN}.md
├── Bugs/BUG-{NNN}.md
└── Sprints/{YYYY-WW}.md  # ISO week
```

## Ticket Frontmatter

```yaml
---
type: epic|story|task|bug
id: TASK-001
status: IN_PROGRESS
priority: P0|P1|P2|P3        # P0=critical, P3=nice-to-have
project: ProjectName
parent: STORY-002             # story→epic, task→story
assignee: claude|user|name
sprint: 2026-W13
created: 2026-03-25
updated: 2026-03-25
labels: [frontend, api]
linked: [TASK-003, BUG-007]
estimate: 2h|1d|3d
---
```

## Ticket Body

```markdown
## Summary
{one-line description}

## Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}

## Notes
{context, links, technical details}

## Activity Log
- {YYYY-MM-DD HH:MM} Status → {NEW_STATUS}: {reason}
```

## Bug Body

```markdown
## Summary
{one-line description}

## Reproduction
1. {step 1}
2. {step 2}
- **Expected:** {what should happen}
- **Actual:** {what happens}
- **Error:** `{error message}`

## Debug Trail
- {HH:MM} Hypothesis: {theory}
- {HH:MM} Tested: {attempt}
- {HH:MM} Result: {outcome}

## Root Cause
{why it happened}

## Fix
{change} → `{file:line}`

## Prevention
{how to avoid}

## Activity Log
- {YYYY-MM-DD HH:MM} Status → {NEW_STATUS}: {reason}
```

## Board Dashboard (`_board.md`)

```markdown
---
type: board
updated: 2026-03-25
---
# Board

## Sprint: 2026-W13 (Mar 24–30)
**Goal:** {sprint goal}

| Status | Tickets |
|--------|---------|
| TODO | [[TASK-012]], [[STORY-005]] |
| IN_PROGRESS | [[TASK-013]], [[BUG-004]] |
| IN_REVIEW | [[TASK-011]] |
| DONE | [[TASK-010]], [[BUG-003]] |
| BLOCKED | [[TASK-009]] — waiting on X |

## Backlog (top 10)
| ID | Type | Priority | Summary |
|----|------|----------|---------|

## Metrics
- **Velocity:** {done} / {planned}
- **Open bugs:** {count by priority}
- **Blocked:** {count + reasons}
```

## Operations

| # | Rule |
|---|------|
| 1 | **Auto-increment IDs** — read `_counter.md`, increment, write back |
| 2 | **Update `_board.md`** on every status change |
| 3 | **Bidirectional links** — parent↔child both reference each other |
| 4 | **Log all transitions** — Activity Log with timestamp + reason |
| 5 | **Sprint default** — new items → current sprint unless specified |
| 6 | **Auto-create** — implementing something? Create TASK if none exists |
| 7 | **Auto-close** — finished → DONE with delivery summary |
| 8 | **Carry over** — incomplete at sprint boundary → next sprint |

## When to Create Tickets

| Situation | Action |
|-----------|--------|
| User describes feature | Create STORY + child TASKs |
| User reports bug | Create BUG |
| Discover bug while working | Create BUG, link to current work |
| Large initiative | Create EPIC → STORYs |
| "Track this" / "add to board" | Appropriate ticket type |
| Starting implementation | Create TASK if none exists |

## Housekeeping

- **Archive:** DONE >2 weeks → move to sprint archive, remove from Board
- **Sprint boundary:** Archive completed, create new sprint, carry over incomplete
