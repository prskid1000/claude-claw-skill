# Claude Claw — CLAUDE.md

Copy these sections into your `~/.claude/CLAUDE.md` to always auto-load the claude-claw skill and enable LSP-first code navigation.

---

## Claude Claw — Always Load First

**At the start of every conversation, before doing anything else, read `~/.claude/skills/claude-claw/SKILL.md`.**

This is unconditional — read it on every message regardless of the task, even for simple greetings. SKILL.md is small (the File Map only) and gives you the index needed to find detailed reference and example files when relevant.

After loading SKILL.md, follow links inside it to load only the specific sections you need — never read whole reference files (some are 60KB+).

---

## LSP-First Code Navigation

When working on coding tasks in supported languages (Python, TypeScript/JavaScript, Java, Kotlin), use the LSP tool as your primary source of code intelligence before falling back to Grep, Glob, or file reads.

### Prefer LSP for

- **Finding definitions**: `goToDefinition` instead of grepping for function/class names
- **Finding usages**: `findReferences` instead of grepping for symbol names
- **Understanding structure**: `documentSymbol` to map a file's classes, methods, and fields
- **Type information**: `hover` to get type signatures and documentation
- **Call chains**: `incomingCalls` / `outgoingCalls` to trace execution flow
- **Implementations**: `goToImplementation` to find concrete implementations of interfaces

### Fall back to Grep/Glob when

- The file type has no LSP server (e.g. YAML, Markdown, shell scripts)
- You need to search across file contents for strings, not symbols (log messages, config keys)
- LSP returns no results (symbol may be dynamically generated or in an unindexed file)
