**Before responding to ANY user request, ensure the claude-claw skill is loaded into this conversation.**

If `SKILL.md` content from the claude-claw skill is not visible in your context, load it by invoking: `Skill(skill: "claude-claw")`. Once loaded, it stays in context for the rest of the session.

All Python deps live in a skill-local venv at `~/.claude/skills/claude-claw/.venv/`. The `claw` CLI on PATH is a shim to that venv — never `pip install claw` into system Python. `scripts/healthcheck.py --install` creates the venv if missing; `--recreate-venv` wipes and rebuilds it.

**Scope of the skill venv:** use it for *skill-level* Python work — claw commands, ad-hoc scripts that reach for claw's libs (pymupdf, openpyxl, lxml, etc.), one-off import probes, debugging claw internals. Path:

- Windows: `~/.claude/skills/claude-claw/.venv/Scripts/python.exe`
- POSIX: `~/.claude/skills/claude-claw/.venv/bin/python`

**Do NOT use it for project work.** If the current working directory is inside a project with its own venv / `pyproject.toml` / `requirements.txt` / poetry / uv / pipenv, project deps go into the project's env — never into the claw venv, and never into system Python. The claw venv is isolated for the skill only; it must not absorb unrelated project dependencies.

When adding a dep that claw itself depends on, update `scripts/claw/pyproject.toml` (correct extra + `all`) and `PACKAGES` in `scripts/healthcheck.py` so `--install` reproduces the setup.

## Working With the Skill

- Follow direct links inside SKILL.md to load only specific sections.
- Never read whole reference files (some are 60KB+).
- Match the user's task to a category in the File Map, then jump to the linked section.

## LSP-First Navigation

When working on code in Python, TypeScript/JavaScript, or Java, use the LSP tool as your primary source of code intelligence before falling back to Grep, Glob, or file reads.

- **Prefer LSP for:**
  - Finding definitions — `goToDefinition` instead of grepping for function/class names
  - Finding usages — `findReferences` instead of grepping for symbol names
  - Understanding structure — `documentSymbol` to map a file's classes, methods, fields
  - Type information — `hover` for type signatures and documentation
  - Call chains — `incomingCalls` / `outgoingCalls` to trace execution flow
  - Implementations — `goToImplementation` for concrete implementations of interfaces
- **Fall back to Grep/Glob when:**
  - File type has no LSP server (YAML, Markdown, shell scripts)
  - Searching for strings in file contents, not symbols (log messages, config keys)
  - LSP returns no results (symbol may be dynamically generated or in an unindexed file)

## Windows Subprocess Note

On Windows, npm/scoop/winget-installed CLIs are `.cmd` / `.bat` shims that `subprocess.run(["tool", ...])` cannot find directly. Always resolve the full path with `shutil.which()` first:

```python
import shutil, subprocess

def run(tool: str, *args: str, **kwargs):
    """Run any CLI tool, resolving Windows .cmd shims via PATH."""
    bin_path = shutil.which(tool)
    if not bin_path:
        raise FileNotFoundError(f"{tool} not in PATH")
    return subprocess.run([bin_path, *args], capture_output=True, text=True, **kwargs)

# Works for gws, clickup, npx, pandoc, magick, ffmpeg, etc.
run("gws", "drive", "files", "list")
run("clickup", "task", "view", "ABC-123")
```
