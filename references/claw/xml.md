# `claw xml` — XML Reference

CLI wrapper over lxml.

## Contents
- [XPath](#xpath) · [Transform](#transform) · [Formatting](#format)

---

## XPath
### `xpath`
```bash
claw xml xpath <SRC> <EXPRESSION> [--json]
```

## Transform
### `xslt`
```bash
claw xml xslt <SRC> <STYLESHEET> --out <OUT> [--force]
```

## Formatting
### `fmt`
```bash
claw xml fmt <SRC> --out <OUT> [--force]
```

---

## Quick Reference
| Task | Command |
|------|---------|
| XPath Query | `claw xml xpath f.xml "//root/node/text()"` |
| Pretty Print | `claw xml fmt f.xml --out pretty.xml` |
| XSLT | `claw xml xslt f.xml style.xsl --out res.xml` |
