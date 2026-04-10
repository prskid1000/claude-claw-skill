# [Tool/Library Name] Reference

<!--
TEMPLATE — How to add a new reference file:

1. Copy this file → references/[your-topic].md
2. Replace all [bracketed] placeholders
3. Structure: Critical Rules → numbered API sections (## 1.1, ## 1.2, ...) → Quick Reference table
4. Keep it agent-friendly: tabular data, code blocks, no prose paragraphs
5. Update SKILL.md File Map:
     - Pick the matching task category (CREATE / READ / EDIT / etc.) or add a new one
     - Add the file with one sub-bullet per H2 section in this format:
         - Ref:
           - [Descriptive label of section](references/your-topic.md#anchor)
           - ... (one bullet per ## heading)
     - Anchor format: lowercase, spaces → hyphens, strip special chars
6. Add tool's pip / npm package to scripts/healthcheck.py PACKAGES or CLI_TOOLS dict
7. Add an install entry to references/setup.md (matching numbered section)

Naming convention: lowercase-kebab-case.md (e.g. pdf-tools.md, gws-cli.md)
-->

## Contents

- [Critical Rules](#critical-rules)
- [Section 1](#section-1)
- [Section 2](#section-2)
- [Quick Reference](#quick-reference)

---

## Critical Rules

<!-- List 3-8 rules that prevent common mistakes. Number them. -->

1. **[Rule]** — [why it matters]
2. **[Rule]** — [why it matters]

---

## [Section 1]

<!-- Group by operation type (create, read, update, delete) or by sub-tool. -->

### [Sub-operation]

```python
# minimal working example
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `param` | `str` | [what it does] |

---

## [Section 2]

<!-- Repeat section pattern as needed -->

---

## Quick Reference

<!-- One-liner cheatsheet table for the most common operations -->

| Task | Code / Command |
|------|----------------|
| [common task] | `[one-liner]` |
