# [Task Name] Examples

<!--
TEMPLATE — How to add a new example file:

1. Copy this file → examples/[your-topic].md
2. Replace all [bracketed] placeholders
3. Structure: TOC → numbered workflows, each self-contained
4. Every code block must be copy-paste runnable (imports, paths, error handling)
5. Add the new file to skill.md Examples table
6. Cross-reference the matching reference file (don't duplicate API docs)

Naming convention: lowercase-kebab-case.md (e.g. pdf-workflows.md, email-workflows.md)
-->

## Contents

- [1. Basic Workflow](#1-basic-workflow)
- [2. Styled / Advanced](#2-styled--advanced)
- [3. End-to-End Pipeline](#3-end-to-end-pipeline)

> **API reference:** See [references/[matching-reference].md](../references/[matching-reference].md)
>
> **Windows:** See [skill.md § Windows Notes](../skill.md#windows-notes) for subprocess setup.

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
