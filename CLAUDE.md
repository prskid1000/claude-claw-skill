# Claude Claw — CLAUDE.md

Copy this section into your `~/.claude/CLAUDE.md` to enable LSP-first code navigation.

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
