# Claude Historian Reference

> MCP-based conversation history search. Installed via plugin: `claude-historian@claude-emporium`.

---

## CRITICAL RULES

1. **All tools are MCP tools** — called as `mcp__plugin_claude-historian_historian__<tool_name>`, NOT as Python imports.
2. **`scope` controls what to search** — use the right scope for the job (see table below).
3. **`detail_level` controls response size** — start with `"summary"`, only use `"detailed"` or `"raw"` if you need more.
4. **`query` is a free-text search string** — it matches against conversation content, not exact field names.

---

## Tools Reference

### search_conversations — Full-text search across all past sessions

**Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | YES | — | Free-text search query |
| `scope` | enum | no | `"all"` | What to search (see scope table below) |
| `detail_level` | enum | no | `"summary"` | `"summary"`, `"detailed"`, or `"raw"` |
| `limit` | number | no | `10` | Max results to return |
| `project` | string | no | — | Filter by project name |
| `timeframe` | string | no | — | `"today"`, `"week"`, or `"month"` |

**Scope values:**
| Scope | Searches | When to use |
|-------|----------|-------------|
| `"all"` | Everything | General search, not sure where to look |
| `"conversations"` | User/assistant messages | Find past discussions about a topic |
| `"files"` | File reads/writes/edits | Find past work on specific files |
| `"errors"` | Bash errors, tool failures | Find past error occurrences |
| `"plans"` | Plan mode content | Find past architectural decisions |
| `"config"` | Config/settings changes | Find past setup work |
| `"tasks"` | Task lists | Find past task planning |
| `"similar"` | Similar queries | Find questions like this one |
| `"sessions"` | Session metadata | Browse session history |
| `"tools"` | Tool usage patterns | Find how tools were used |
| `"memories"` | Memory operations | Find past memory saves |

**Examples:**
```
# Search for past work on authentication
mcp__plugin_claude-historian_historian__search_conversations(query="authentication login flow")

# Search only errors, this week
mcp__plugin_claude-historian_historian__search_conversations(query="connection refused", scope="errors", timeframe="week")

# Search past plans about database migration
mcp__plugin_claude-historian_historian__search_conversations(query="database migration", scope="plans", detail_level="detailed")

# Search files related to a specific module
mcp__plugin_claude-historian_historian__search_conversations(query="gws-cli.md", scope="files", limit=5)

# Search in a specific project
mcp__plugin_claude-historian_historian__search_conversations(query="deploy", project="routemagic")
```

---

### find_similar_queries — Find past questions similar to the current one

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | YES | The question to match against past queries |

**Example:**
```
mcp__plugin_claude-historian_historian__find_similar_queries(query="how do I upload a file to Google Drive using gws CLI")
```

**Use when:** You want to check if a similar question was asked before (avoids redundant research).

---

### get_error_solutions — Search history for past fixes to similar errors

**Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `error_pattern` | string | YES | — | The error text or pattern to search for |
| `limit` | number | no | `3` | Max solutions to return |

**Examples:**
```
# Find past fixes for a specific error
mcp__plugin_claude-historian_historian__get_error_solutions(error_pattern="FileNotFoundError: gws")

# Find past fixes for MySQL connection issues
mcp__plugin_claude-historian_historian__get_error_solutions(error_pattern="connection refused mysql", limit=5)
```

**Use when:** You encounter an error and want to check if it was solved before.

---

### find_file_context — Find past work done on a specific file

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `filepath` | string | YES | Path to the file (relative or absolute) |

**Examples:**
```
# What was done to this file in past sessions?
mcp__plugin_claude-historian_historian__find_file_context(filepath="references/gws-cli.md")

# Check past work on a specific source file
mcp__plugin_claude-historian_historian__find_file_context(filepath="src/api/auth.py")
```

**Use when:** You want context about what changes were made to a file across past sessions.

---

### find_tool_patterns — How tools were used in past sessions

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | string | YES | Name of the tool to search for |

**Examples:**
```
# How was the MySQL MCP tool used before?
mcp__plugin_claude-historian_historian__find_tool_patterns(tool_name="mcp__mcp_server_mysql__mysql_query")

# How was gws used in past sessions?
mcp__plugin_claude-historian_historian__find_tool_patterns(tool_name="gws")

# How was the code review graph used?
mcp__plugin_claude-historian_historian__find_tool_patterns(tool_name="build_or_update_graph_tool")
```

**Use when:** You want to learn from past tool usage patterns.

---

### search_plans — Search past implementation plans

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | YES | Plan topic to search for |

**Examples:**
```
mcp__plugin_claude-historian_historian__search_plans(query="API rate limiting")
mcp__plugin_claude-historian_historian__search_plans(query="database schema migration")
```

**Use when:** Before planning a new feature, check if a similar plan already exists.

---

### list_recent_sessions — Browse recent sessions

**Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `limit` | number | no | `10` | How many sessions to list |

**Example:**
```
mcp__plugin_claude-historian_historian__list_recent_sessions(limit=20)
```

---

### extract_compact_summary — Get a compact summary of a session

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | YES | The session ID to summarize (get from `list_recent_sessions`) |

**Example:**
```
# First list sessions to get IDs
mcp__plugin_claude-historian_historian__list_recent_sessions(limit=5)

# Then summarize a specific session
mcp__plugin_claude-historian_historian__extract_compact_summary(session_id="abc123-def456")
```

---

## Auto-Triggers (Plugin Hooks)

The plugin installs 4 hooks that fire automatically — no manual invocation needed:

| Hook | Fires when | What it does |
|------|------------|--------------|
| `pre-websearch` | Before WebSearch/WebFetch | Checks history first, skips redundant web lookups |
| `pre-planning` | Before EnterPlanMode | Searches past plans and architectural decisions |
| `pre-task` | Before subagent launch | Checks past tool patterns for the task type |
| `post-error` | After Bash error (exit code > 0) | Searches history for past solutions to similar errors |

---

## How It Works

- **No persistent index** — scans JSONL files fresh on every query
- **Two-phase search** — cheap string pre-filter, then full JSON parse on hits
- **Parallel processing** across projects
- **Zero external dependencies** (Node.js only)
- **Data source:** reads from `~/.claude/projects/**/*.jsonl`

---

## Quick Decision Tree

**"Have I done this before?"**
-> `search_conversations(query="...", scope="all")`

**"Have I seen this error before?"**
-> `get_error_solutions(error_pattern="the error text")`

**"What did I do to this file last time?"**
-> `find_file_context(filepath="path/to/file")`

**"Did I already plan something like this?"**
-> `search_plans(query="feature description")`

**"How did I use this tool before?"**
-> `find_tool_patterns(tool_name="tool_name")`

**"What happened in my recent sessions?"**
-> `list_recent_sessions(limit=10)` then `extract_compact_summary(session_id="...")`
