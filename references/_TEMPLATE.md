# [Tool / Library Name] Reference

<!--
TEMPLATE — How to add a new reference file:

1. Copy this file → references/[your-topic].md
2. Replace all [bracketed] placeholders.
3. STRUCTURE (do not reorder):
     H1 title → Contents tree → Critical Rules → numbered API sections → Quick Reference
4. ONLY the Contents list at the top is in decision-tree format (see SKILL.md
   § Decision-Tree List Format). Each top-level bullet is a user-intent VERB
   (CREATE / READ / EDIT / CONFIGURE / TROUBLESHOOT …). Nested bullets link to
   the H2 section anchors that fulfil that intent. Do NOT force this shape on
   the body — code blocks, tables, and API detail stay in their natural form.
5. Every anchor linked from the Contents tree AND from SKILL.md must exist as
   a matching H2 in this file. Anchor convention: lowercase kebab-case, strip
   punctuation, spaces → hyphens. Number body sections as `## 1.1`, `## 1.2`
   within a topic group.
6. Do NOT duplicate content that lives elsewhere — link to the authoritative
   source instead. Windows subprocess helper, installation steps, cross-tool
   workflows etc. already have homes.
7. Update SKILL.md File Map:
     - Find the matching task category (or add a new one).
     - Under the matching option, list this file in a `- Ref:` block with one
       sub-bullet per H2 section (or the compact `·`-separated form for dense
       nodes).
8. Add tool's pip / npm package to scripts/healthcheck.py PACKAGES or
   CLI_TOOLS dict, and an install entry to references/setup.md.

Naming convention: lowercase-kebab-case.md (e.g. pdf-tools.md, gws-cli.md).
-->

## Contents

<!--
Decision-tree shape. Top-level bullets are user intents (verbs, caps). Nested
bullets link to H2 anchors in this file that fulfil that intent. Keep labels
descriptive (3–8 words) — don't just repeat the heading text.
-->

- **VERB a thing**
  - [First action in that branch](#11-first-action)
  - [Second action](#12-second-action)
- **ANOTHER VERB**
  - [Something else](#21-something-else) · [And another](#22-and-another)

---

## Critical Rules

<!-- 3–8 numbered rules that prevent common mistakes. -->

1. **[Rule]** — [why it matters].
2. **[Rule]** — [why it matters].

---

## 1.1 First Action

<!-- One H2 per discrete capability. Anchor must match the Contents link exactly. -->

```python
# minimal working example
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `param` | `str` | [what it does] |

---

## 1.2 Second Action

---

## 2.1 Something Else

---

## 2.2 And Another

---

## Quick Reference

<!-- One-liner cheatsheet table. Optional. -->

| Task | Code / Command |
|------|----------------|
| [common task] | `[one-liner]` |
