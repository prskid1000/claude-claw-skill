# `claw completion` — Shell Integration Reference

CLI tool for generating shell autocompletion scripts.

## Contents

- **SHELLS**
  - [Bash](#11-bash) · [Zsh](#12-zsh) · [Fish](#13-fish) · [PowerShell](#14-pwsh)

---

## Critical Rules

1. **Static Generation** — Completions are generated statically based on the current CLI tree.
2. **Reload Required** — You must source the output or restart your shell to activate changes.
3. **Lazy Loading** — Completions for lazy-loaded nouns are included in the map.

---

## 1.1 bash
Generate the Bash completion script.
```bash
claw completion bash
```

## 1.2 zsh
Generate the Zsh completion script.
```bash
claw completion zsh
```

## 1.3 fish
Generate the Fish completion script.
```bash
claw completion fish
```

## 1.4 pwsh
Generate the PowerShell completion script.
```bash
claw completion pwsh
```

---

## Quick Reference
| Task | Command |
|------|---------|
| Bash Install | `claw completion bash > ~/.claw-completion.sh && echo "source ~/.claw-completion.sh" >> ~/.bashrc` |
| Zsh Install | `claw completion zsh > /usr/local/share/zsh/site-functions/_claw` |
| Fish Install | `claw completion fish > ~/.config/fish/completions/claw.fish` |
