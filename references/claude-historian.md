# Claude Historian Reference

> MCP-based conversation history search. Installed via plugin: `claude-historian@claude-emporium`.

## MCP Tools

All tools are prefixed with `mcp__plugin_claude-historian_historian__`.

### search_conversations
Full-text search across all past Claude Code sessions.
- `query` (string) — search query
- `scope` (enum: all/conversations/files/errors/plans/config/tasks/similar/sessions/tools/memories) — default "all"
- `detail_level` (enum: summary/detailed/raw) — default "summary"
- `limit` (number) — default 10
- `project` (string, optional) — filter by project name
- `timeframe` (string, optional) — today/week/month

### find_similar_queries
Find past questions similar to the current one.
- `query` (string) — the question to match against

### get_error_solutions
Search history for past fixes to similar errors.
- `error_pattern` (string) — the error text or pattern
- `limit` (number) — default 3

### find_file_context
Find past work done on a specific file.
- `filepath` (string) — path to the file

### find_tool_patterns
How tools were used in past sessions.
- `tool_name` (string) — name of the tool

### search_plans
Search past implementation plans.
- `query` (string) — plan topic to search for

### list_recent_sessions
Browse recent sessions.
- `limit` (number) — how many sessions to list

### extract_compact_summary
Get a compact summary of a session.
- `session_id` (string) — the session to summarize

## Auto-Triggers (Plugin Hooks)

The plugin installs 4 hooks that fire automatically:

| Hook | When | Action |
|------|------|--------|
| pre-websearch | Before WebSearch/WebFetch | Checks history first, skips redundant lookups |
| pre-planning | Before EnterPlanMode | Searches past plans/architectural decisions |
| pre-task | Before subagent launch | Checks past tool patterns |
| post-error | After Bash error | Searches history for past solutions |

## How It Works

- No persistent index — scans JSONL files fresh on every query
- Two-phase: cheap string pre-filter, then full JSON parse for hits
- Parallel processing across projects
- Zero external dependencies (Node.js only)
- Reads from `~/.claude/projects/**/*.jsonl`

## When to Use

- Before starting work: "What did I do last time on this feature?"
- On errors: "Have I seen this error before?"
- Before planning: "Did I already plan something similar?"
- File context: "What changes were made to this file in past sessions?"
