# [Task Name] Examples

<!--
TEMPLATE — How to add a new example file:

1. Copy this file → examples/[your-topic].md
2. Replace all [bracketed] placeholders.
3. STRUCTURE: Contents tree → numbered self-contained workflows (## H2 per workflow).
4. ONLY the Contents list at the top is in decision-tree format (see SKILL.md
   § Decision-Tree List Format). Body workflows stay as natural runnable code
   blocks — don't force the tree shape onto code snippets.
5. Every code block must be copy-paste runnable: explicit imports, absolute
   paths, error handling where meaningful.
6. Do NOT duplicate API reference content. Examples show end-to-end working
   code; the matching reference has the API surface.
7. Update SKILL.md File Map:
     - Under the matching option's `- Ex:` block, add one bullet per H2
       workflow:
         - Ex:
           - [Descriptive label of what the workflow builds](examples/your-topic.md#anchor)
           - … (one bullet per ## heading)

Naming convention: lowercase-kebab-case.md (e.g. pdf-workflows.md, email-workflows.md).
-->

## Contents

<!--
Decision-tree shape, keyed by user intent. Group H2 workflows under the verb
that describes what each one accomplishes.
-->

- **BUILD**
  - [Basic workflow](#1-basic-workflow)
  - [Styled / advanced variant](#2-styled--advanced)
- **ORCHESTRATE**
  - [End-to-end pipeline](#3-end-to-end-pipeline)

> **API reference:** See [references/[matching-reference].md](../references/[matching-reference].md).

---

## 1. Basic Workflow

<!-- Simplest possible working example. Input → output in <20 lines. -->

```python
# [description]
from [lib] import [class]

[minimal working code]
print("Done: /tmp/output.xyz")
```

---

## 2. Styled / Advanced

<!-- Same task with formatting, styling, or additional features. -->

```python
# [description]
[code with styling, error handling, etc.]
```

---

## 3. End-to-End Pipeline

<!-- Multi-step workflow: read input → transform → write output → deliver. -->

```python
# [description]
# Step 1: Read input
# Step 2: Transform
# Step 3: Write output
# Step 4: Deliver (e.g. gws drive upload)
```
