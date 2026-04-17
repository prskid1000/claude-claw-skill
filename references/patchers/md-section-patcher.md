# Markdown Section Patcher

Script: `~/.claude/skills/claude-claw/scripts/patchers/md-section-patcher.py`

Idempotent injector for a named block of content into any markdown file. The
block lives between HTML comment markers, so markdown viewers render nothing;
the patcher fully owns what's between them and leaves everything outside
untouched.

## Contents

- **APPLY / UPDATE a managed section** — inject on first run, update on drift
  - [Markers (how the block is delimited)](#markers)
  - [Usage (`apply` / `status` / `remove`)](#usage)
  - [Worked example (claude-claw block in `~/.claude/CLAUDE.md`)](#worked-example)
- **INSPECT sync state**
  - [Status exit codes for CI](#status-exit-codes)
- **REMOVE a section**
  - [Strip the named block cleanly](#remove)

---

## Critical Rules

1. **Whole file is trusted.** The patcher reads and rewrites the target file in
   place. Only content between the markers is overwritten; the rest is
   preserved byte-for-byte.
2. **Markers must be unique per file.** Use a distinct `--section` name for each
   managed block you inject. Two apply runs with the same name will collapse
   into one block.
3. **Source file wins.** `apply` treats the `--source` file as the authoritative
   body. Any manual edits made between markers will be overwritten on next
   `apply`.
4. **Unix-style LF writes.** Python writes with the platform default; on Windows
   git may re-normalize. Add the managed file to `.gitattributes` with
   `text eol=lf` if you need deterministic checksums in CI.

---

## Markers

Each managed section is delimited by a pair of HTML comments:

```markdown
<!-- SECTION_NAME:begin -->
...managed content, fully owned by the patcher...
<!-- SECTION_NAME:end -->
```

- `SECTION_NAME` comes from the `--section` argument (arbitrary string, no
  whitespace recommended).
- Markers render to nothing in any markdown viewer.
- Content between markers is stripped and re-written on every `apply`.
- Content outside markers is never touched.

---

## Usage

```bash
PATCHER=~/.claude/skills/claude-claw/scripts/patchers/md-section-patcher.py

# Inject or update a named section
python $PATCHER apply \
    --target ~/.claude/CLAUDE.md \
    --section claude-claw \
    --source ~/.claude/skills/claude-claw/blocks/claude-md-snippet.md

# Check whether a section is present / in-sync with a source
python $PATCHER status \
    --target ~/.claude/CLAUDE.md \
    --section claude-claw \
    --source ~/.claude/skills/claude-claw/blocks/claude-md-snippet.md

# Remove a section (leaves surrounding content intact)
python $PATCHER remove \
    --target ~/.claude/CLAUDE.md \
    --section claude-claw
```

**Behaviour of `apply`:**
- Target missing → creates it with just the block.
- Target exists, no matching markers → **prepends** the block to the top of the
  file.
- Target exists with matching markers, content in sync → no write.
- Target exists with matching markers, content drifted → rewrites the block
  only.

**Behaviour of `status`:** prints one of `[PRESENT]`, `[MISSING]`, `[IN-SYNC]`,
`[DRIFTED]`. Exit code signals the state — see [below](#status-exit-codes).

**Behaviour of `remove`:** deletes the block (markers and all). Collapses
triple-or-more consecutive blank lines back to a double blank to avoid
ragged gaps where the section used to be.

---

## Worked Example

Scenario: the `claude-claw` skill wants its LSP-first instructions to live at
the top of the user's global `~/.claude/CLAUDE.md`, but only inside a managed
block so hand-written content around it survives edits.

1. Author the canonical snippet once — lives at [`references/patchers/claude-md-block.md`](claude-md-block.md):

   ```markdown
   # references/patchers/claude-md-block.md
   Before responding, ensure the claude-claw skill is loaded (Skill(claude-claw)).
   … LSP-first navigation rules, Windows subprocess helper, etc.
   ```

2. Run `apply`:

   ```bash
   python ~/.claude/skills/claude-claw/scripts/patchers/md-section-patcher.py apply \
       --target ~/.claude/CLAUDE.md \
       --section claude-claw \
       --source ~/.claude/skills/claude-claw/references/patchers/claude-md-block.md
   ```

3. The target now contains:

   ```markdown
   <!-- claude-claw:begin -->
   Before responding, ensure the claude-claw skill is loaded (Skill(claude-claw)).
   …
   <!-- claude-claw:end -->

   <everything the user wrote by hand, unchanged>
   ```

4. On the next upgrade, edit the snippet file and re-run `apply`. Only the
   managed block updates; hand-written content around it is preserved.

5. To fully opt out: `remove --target ~/.claude/CLAUDE.md --section claude-claw`.

---

## Status Exit Codes

| Exit | Meaning | CI use |
|------|---------|--------|
| `0` | Success — block present and (if `--source` given) in-sync with source. | Proceed. |
| `1` | Handled error (missing source file, bad args). | Abort, inspect stderr. |
| `3` | Block missing OR drifted from source. | Fail the gate; run `apply` to heal. |

The `3` code is convenient for CI pipelines that want to enforce "managed
blocks stay in sync" without a full re-write step — run `status`, fail on 3.

---

## Remove

`remove` is idempotent:

- Target doesn't exist → `[PASS]` no-op.
- Markers absent → `[PASS]` no-op.
- Markers present → strips them, collapses excess blank lines.

Use it when retiring a managed block (e.g. after deleting a skill that
injected its own CLAUDE.md snippet).

---

## Quick Reference

| Task | Command |
|------|---------|
| Inject / update a block | `apply --target FILE --section NAME --source BODY_FILE` |
| Check sync state | `status --target FILE --section NAME [--source BODY_FILE]` |
| Strip a block | `remove --target FILE --section NAME` |
| CI gate (exit 3 on drift) | `status ...; [ $? -eq 0 ] \|\| fail` |
