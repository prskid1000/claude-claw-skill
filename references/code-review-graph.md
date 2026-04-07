# Code Review Graph — Structural Code Analysis (MCP)

> Builds a knowledge graph of your codebase using Tree-sitter AST parsing. Gives AI precise context — blast radius, dependencies, test coverage — so it reads only what matters.
> Repo: https://github.com/tirth8205/code-review-graph

---

## Install

```bash
pip install code-review-graph                        # requires Python 3.10+
code-review-graph install --platform claude-code     # configure MCP
code-review-graph build                              # parse codebase (run in project dir)
```

Initial build: ~10 seconds for 500 files. After that, incremental updates in <2 seconds via git hooks.

### Update
```bash
pip install --upgrade code-review-graph
```

### MCP config (~/.claude.json — auto-created by install)
```json
{
  "mcpServers": {
    "code-review-graph": {
      "type": "stdio",
      "command": "code-review-graph",
      "args": ["serve"]
    }
  }
}
```

---

## CLI Commands

```bash
code-review-graph build            # parse entire codebase
code-review-graph update           # incremental update (changed files only)
code-review-graph status           # graph statistics
code-review-graph watch            # auto-update on file changes
code-review-graph visualize        # generate interactive HTML graph
code-review-graph wiki             # generate markdown wiki from communities
code-review-graph detect-changes   # risk-scored change impact analysis
code-review-graph register <path>  # register repo in multi-repo registry
code-review-graph unregister <id>  # remove repo from registry
code-review-graph repos            # list registered repositories
code-review-graph serve            # start MCP server
```

---

## Slash Commands (Claude Code)

| Command | Description |
|---------|-------------|
| `/code-review-graph:build-graph` | Build or rebuild the code graph |
| `/code-review-graph:review-delta` | Review changes since last commit |
| `/code-review-graph:review-pr` | Full PR review with blast-radius analysis |

---

## 22 MCP Tools

### Graph Management
| Tool | Description |
|------|-------------|
| `build_or_update_graph_tool` | Build or incrementally update the graph |
| `list_graph_stats_tool` | Graph size and health stats |
| `embed_graph_tool` | Compute vector embeddings for semantic search |

### Code Review & Impact Analysis
| Tool | Description |
|------|-------------|
| `get_impact_radius_tool` | Blast radius of changed files — callers, dependents, tests affected |
| `get_review_context_tool` | Token-optimised review context with structural summary |
| `detect_changes_tool` | Risk-scored change impact analysis for code review |

### Graph Queries
| Tool | Description |
|------|-------------|
| `query_graph_tool` | Query callers, callees, tests, imports, inheritance relationships |
| `semantic_search_nodes_tool` | Search code entities by name or meaning |
| `find_large_functions_tool` | Find functions/classes exceeding a line-count threshold |

### Execution Flows
| Tool | Description |
|------|-------------|
| `list_flows_tool` | List execution flows sorted by criticality |
| `get_flow_tool` | Get details of a single execution flow |
| `get_affected_flows_tool` | Find flows affected by changed files |

### Code Communities & Architecture
| Tool | Description |
|------|-------------|
| `list_communities_tool` | List detected code communities (clusters of related code) |
| `get_community_tool` | Get details of a single community |
| `get_architecture_overview_tool` | Architecture overview from community structure |

### Refactoring
| Tool | Description |
|------|-------------|
| `refactor_tool` | Rename preview, dead code detection, suggestions |
| `apply_refactor_tool` | Apply a previously previewed refactoring |

### Documentation
| Tool | Description |
|------|-------------|
| `get_docs_section_tool` | Retrieve documentation sections |
| `generate_wiki_tool` | Generate markdown wiki from communities |
| `get_wiki_page_tool` | Retrieve a specific wiki page |

### Multi-Repo
| Tool | Description |
|------|-------------|
| `list_repos_tool` | List registered repositories |
| `cross_repo_search_tool` | Search across all registered repos |

---

## How It Works

1. **Parse** — Tree-sitter parses your code into ASTs across 19 languages
2. **Graph** — Nodes (functions, classes, imports) and edges (calls, inheritance, test coverage) stored in SQLite
3. **Blast Radius** — When files change, traces every caller, dependent, and test affected
4. **Minimal Context** — AI reads only the affected files, not the whole project

### Supported Languages (19)
Python, TypeScript/TSX, JavaScript, Vue, Go, Rust, Java, Scala, C#, Ruby, Kotlin, Swift, PHP, Solidity, C/C++, Dart, R, Perl, plus Jupyter notebooks.

---

## Workflow Patterns

### Code review
```
1. get_review_context_tool(changed_files)  -> token-optimised summary
2. get_impact_radius_tool(changed_files)   -> blast radius
3. detect_changes_tool()                   -> risk scores
```

### Understanding architecture
```
1. get_architecture_overview_tool()        -> community-based map
2. list_communities_tool()                 -> code clusters
3. query_graph_tool(node, "callers")       -> who calls what
```

### Refactoring
```
1. refactor_tool("rename", old, new)       -> preview changes
2. apply_refactor_tool(refactor_id)        -> apply
3. refactor_tool("dead_code")             -> find unused code
```

### PR review
```
/code-review-graph:review-pr              -> full blast-radius PR review
```

---

## Benchmarks

| Metric | Result |
|--------|--------|
| Token reduction | **8.2x average** (naive vs graph) |
| Monorepo savings | Up to **49x** (Next.js: 27,700 files -> ~15 read) |
| Build time (500 files) | ~10 seconds |
| Incremental update | <2 seconds |
| Review quality | 1.0 (perfect) vs 0.54 naive |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `command not found` | `pip install code-review-graph` (Python 3.10+) |
| MCP not connecting | Check `~/.claude.json` entry; restart Claude Code |
| Empty graph / no results | Run `code-review-graph build` in the project directory |
| Stale graph | Run `code-review-graph update` or enable `code-review-graph watch` |
| Wrong command format | Use `code-review-graph` not `uvx` if installed via pip |
