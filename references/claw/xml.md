# `claw xml` — XML Operations Reference

CLI wrapper over `lxml` for structured data manipulation. Handles querying, transformation, and validation of XML documents.

## Contents

- **QUERY / EXTRACT**
  - [XPath Query](#11-xpath) · [Streaming XPath](#12-stream-xpath) · [To JSON](#13-to-json)
- **TRANSFORM / FORMAT**
  - [XSLT Transformation](#21-xslt) · [Format (Pretty-Print)](#22-fmt) · [Canonicalization (C14N)](#23-canonicalize)
- **VALIDATE**
  - [Schema Validation](#31-validate)

---

## Critical Rules

1. **Namespace Awareness** — `xpath` automatically registers namespaces found in the root element. Use the registered prefixes in your expressions.
2. **XSLT Version** — Only XSLT 1.0 is supported (limitation of the underlying `libxslt` used by `lxml`).
3. **Security (XXE)** — DTD loading and external entity expansion are disabled by default to prevent XXE attacks.
4. **Large Files** — Use `stream-xpath` for very large XML files that exceed available memory.

---

## 1.1 xpath
Query the XML tree using XPath 1.0. Output as JSON, text, XML, or attribute-only via `--json/--text/--xml/--attr NAME`; `--count` returns a node count. Bind variables with repeatable `--var NAME=VALUE` and namespaces with `--ns PREFIX=URI`. Security flags (off by default): `--allow-undeclared-vars`, `--allow-entities`, `--allow-network`, `--huge-tree`.
```bash
claw xml xpath <SRC> <EXPRESSION> [--json|--text|--xml|--attr NAME|--count] [--var NAME=VAL]... [--ns PREFIX=URI]...
```

## 1.2 stream-xpath
Memory-efficient XPath querying for large files (iterative parsing).
```bash
claw xml stream-xpath <SRC> <EXPRESSION> [--tag <NAME>]
```

## 1.3 to-json
Convert XML structure to a JSON representation.
```bash
claw xml to-json <SRC> [--out <OUT>] [--force]
```

---

## 2.1 xslt
Apply an XSLT stylesheet to the XML document.
```bash
claw xml xslt <SRC> <STYLESHEET> --out <OUT> [--param KEY=VAL] [--force]
```

## 2.2 fmt
Pretty-print XML with configurable indent. `--sort-attrs` gives deterministic attribute order; `--declaration` emits the `<?xml...?>` prolog; `--encoding` sets the output encoding.
```bash
claw xml fmt <SRC> [--indent <INTEGER>] [--sort-attrs] [--declaration] [--encoding <TEXT>] [--out <PATH>]
```

## 2.3 canonicalize
Produce the canonical form (C14N) of the XML document.
```bash
claw xml canonicalize <SRC> [--out <OUT>] [--force]
```

---

## 3.1 validate
Validate `<SRC>` against a schema. Pick one: `--xsd` (XML Schema), `--rng` (RelaxNG XML syntax), `--rnc` (RelaxNG compact syntax), or `--dtd`. Exits 6 on validation failure. `--all-errors` reports every error rather than stopping at the first.
```bash
claw xml validate <SRC> (--xsd <PATH> | --rng <PATH> | --rnc <PATH> | --dtd <PATH>) [--all-errors]
```

---

## Footguns
- **Namespace Mismatch** — If your XPath returns nothing but the element is clearly there, check if the document uses a default namespace (`xmlns="..."`).
- **Entity Resolution** — Validation might fail if the document relies on external DTDs that are blocked by security settings.

## Escape Hatch
Underlying library: `lxml` (Python). For high-performance streaming, consider `xml.etree.ElementTree` or `SAX`.

## Quick Reference
| Task | Command |
|------|---------|
| XPath Search | `claw xml xpath data.xml "//item[@id='1']"` |
| Format XML | `claw xml fmt data.xml --out pretty.xml` |
| To JSON | `claw xml to-json data.xml` |
| XSLT | `claw xml xslt data.xml style.xsl` |
| Validate XSD | `claw xml validate data.xml --xsd schema.xsd` |
