# Web Parsing Reference (lxml + BeautifulSoup4)

> **TL;DR: use `claw html <verb>` / `claw xml <verb>` for common tasks.** See [references/claw/html.md](claw/html.md) and [references/claw/xml.md](claw/xml.md). This reference documents the library APIs (`lxml`, `BeautifulSoup4`) for escape-hatch / advanced workflows not covered by `claw` — XSLT with parameter extensions, RelaxNG / Schematron validation, objectify / ObjectPath, custom ElementBase subclasses, streaming `iterparse`, SoupStrainer partial parsing, and custom encoding recovery via `UnicodeDammit`.

## Contents

- **PARSE / QUERY XML** — `lxml`
  - [Parse, build, serialize, namespaces](#elementtree-api) *(basic cases covered by `claw xml xpath`)*
  - [XPath 1.0 + EXSLT extensions](#xpath-10) *(basic cases covered by `claw xml xpath`)*
  - [XSLT transformations + access control](#xslt-transformations) *(single-file runs covered by `claw xml xslt`)*
  - [XSD / RelaxNG / Schematron / DTD validation](#validation) *(XSD covered by `claw xml validate`)*
  - [Streaming `iterparse`](#iterparse-streaming) *(covered by `claw xml stream-xpath`)*
  - [Custom resolvers, element classes, objectify](#custom-element-classes)
- **PARSE / QUERY HTML** — `lxml.html` (fast) or `BeautifulSoup4` (lenient)
  - [lxml.html — DOM, links, forms, Cleaner, diff](#lxmlhtml) *(links/forms/clean covered by `claw html`)*
  - [BeautifulSoup parsers + navigation + selectors](#beautifulsoup4) *(covered by `claw html select/text/strip/sanitize`)*
  - [Encoding detection — UnicodeDammit / detwingle](#encoding)
- **Escape-hatch recipes** — [XSLT params, custom resolvers, SoupStrainer, schematron, CSS→XPath translation](#escape-hatch-recipes)

## Critical Rules

1. **For everyday CSS-selector scraping, prefer `claw html`.** Drop into `BeautifulSoup` only when you need `UnicodeDammit`, `SoupStrainer`, or multi-valued-attribute customization.
2. **`lxml` is the library for all XML work.** `claw xml` wraps the common verbs; XSLT parameters, RelaxNG, Schematron, and custom resolvers require direct library access.
3. **Always declare namespaces in XPath.** `root.xpath("//ns:elem", namespaces={"ns": "..."})` — no `xmlns` auto-discovery.
4. **`recover=True` masks errors.** Only set it for the escape-hatch of salvaging broken XML; otherwise let `XMLSyntaxError` propagate.

---

## lxml

```python
import lxml.etree as etree
import lxml.html
```

### ElementTree API

> `claw xml xpath | fmt | canonicalize | to-json` cover the common read / serialize path — see [claw/xml.md](claw/xml.md). Below: API reference for in-code use.

Parse: `etree.parse(path_or_stream)` → ElementTree · `etree.fromstring(bytes)` → Element · `etree.XML("<root/>")` · wrap: `etree.ElementTree(elem)`.

| Method | Purpose |
|---|---|
| `etree.Element(tag, attrib={...})` | Create element |
| `etree.SubElement(parent, tag)` | Append child |
| `elem.text` / `elem.tail` | Inner text / post-tag text |
| `elem.set(k, v)` / `elem.get(k)` / `elem.attrib` | Attribute R/W |
| `elem.append/insert/remove/replace(child)` | Child mutation |
| `elem.addnext/addprevious(sibling)` | Sibling mutation |
| `elem.getparent/getprevious/getnext()` | Navigation |
| `elem.iter(*tags)` | All descendants (optionally filtered) |
| `elem.iterchildren/itersiblings/iterancestors/iterdescendants/itertext` | Axis iterators |

E-factory (declarative construction):

```python
from lxml.builder import E
html = E.html(E.head(E.title("Page")),
              E.body(E.p("Paragraph", {"class": "intro"})))
```

Serialize: `etree.tostring(root, pretty_print=True, encoding="unicode"|"utf-8", method="xml"|"html"|"c14n"|"c14n2", xml_declaration=True)` · `etree.indent(root, space="  ")` (in-place) · `tree.write(path, pretty_print, xml_declaration, encoding)`.

---

### XPath 1.0

> `claw xml xpath` runs XPath 1.0 with namespace + regex support — see [claw/xml.md](claw/xml.md). Below: syntax crib, compiled / parameterized queries, EXSLT.

Common syntax:

| Expression | Purpose |
|---|---|
| `//div` | All `div` descendants |
| `//div[@class='main']` | Attribute filter |
| `//div/p/text()` | Text content |
| `//a/@href` | Attribute values |
| `count(//p)` | Count (float) |
| `//p[position()>2]` | Positional |
| `//p[last()]` | Last |
| `//div[contains(@class,'item')]` | contains |
| `//div[starts-with(@id,'sec')]` | starts-with |
| `//h1 \| //h2 \| //h3` | Union |
| `//div[not(@hidden)]` | Negation |
| `normalize-space(//title)` | Normalize whitespace |
| `string(//title)` | String value |

Axes: `self`, `child`, `parent`, `ancestor`, `ancestor-or-self`, `descendant`, `descendant-or-self`, `following`, `following-sibling`, `preceding`, `preceding-sibling`, `attribute`, `namespace`.

Compiled / parameterized (escape hatch — `claw` accepts literal expressions only):

```python
find = etree.XPath("//div[@class=$cls]")
results = find(root, cls="main")
find = etree.ETXPath("//{http://ns.example.com}tag")   # namespace-aware
```

EXSLT namespaces: `regexp`, `set`, `math`, `string`, `date`.

```python
ns = {"re": "http://exslt.org/regular-expressions"}
root.xpath("//a[re:test(@href, 'https?://')]", namespaces=ns)
```

---

### XSLT Transformations

> Use `claw xml xslt` for single-file transforms. This API is the escape hatch for passing parameters, access control, and profiling.

| Call | Purpose |
|---|---|
| `etree.XSLT(xslt_tree)` | Compile stylesheet |
| `transform(doc)` | Apply |
| `transform(doc, param=etree.XSLT.strparam("value"))` | Pass string parameter |
| `transform(doc, profile_run=True)` → `result.xslt_profile` | Profiling output |
| `transform.error_log` | Diagnostics |

Access control (sandboxing):

```python
ac = etree.XSLTAccessControl(read_file=True, write_file=False,
                              create_dir=False, read_network=False,
                              write_network=False)
transform = etree.XSLT(xslt_tree, access_control=ac)
```

---

### Validation

> `claw xml validate` covers XSD — see [claw/xml.md](claw/xml.md). RelaxNG, Schematron, and DTD stay in the library.

| Schema type | Constructor | Notes |
|---|---|---|
| XSD | `etree.XMLSchema(etree.parse("schema.xsd"))` | Covered by `claw xml validate` |
| RelaxNG | `etree.RelaxNG(etree.parse("schema.rng"))` | Compact syntax via `RelaxNG.from_rnc_string(...)` |
| Schematron | `etree.Schematron(etree.parse("rules.sch"))` | `validation_report` returns SVRL XML |
| DTD | `etree.DTD("schema.dtd")` | — |

All four share the same `.validate(doc)` (→ bool), `.assertValid(doc)` (raises), `.error_log` surface. Parse-time validation: `etree.XMLParser(schema=XMLSchema_instance)`.

---

### lxml.html

> `claw html select | text | strip | sanitize | absolutize | rewrite` wrap the common HTML surface — see [claw/html.md](claw/html.md). Below: API signatures for escape-hatch use.

Parsers: `lxml.html.fromstring(html)` · `.parse(url_or_path)` · `.document_fromstring(html)` · `.fragment_fromstring(html)` · `.fragments_fromstring(html)`.

Element methods: `.text_content()` (recursive) · `.drop_tree()` · `.drop_tag()` (keep children) · `.classes` (set) · `.base_url`.

Links: `doc.make_links_absolute(base_url)` · `doc.resolve_base_href()` · `for element, attribute, link, pos in doc.iterlinks(): ...` · `doc.rewrite_links(lambda href: ...)`.

#### Forms

Escape hatch — not wrapped by `claw html`.

```python
for form in doc.forms:
    print(form.action, form.method, form.fields)
    form.fields["input_name"] = "value"
```

#### Cleaner

Covered by `claw html sanitize`; requires `pip install lxml_html_clean` (separated from lxml in 5.2+).

```python
from lxml_html_clean import Cleaner
cleaner = Cleaner(
    scripts=True, javascript=True, comments=True,
    style=False, links=False, meta=True,
    page_structure=False, processing_instructions=True,
    embedded=True, frames=True, forms=False,
    annoying_tags=True, remove_tags=None,
    remove_unknown_tags=True, safe_attrs_only=True,
    safe_attrs=frozenset(["href","src","alt","title","class","id"]),
    add_nofollow=False, host_whitelist=(), whitelist_tags=set(),
)
clean_html = cleaner.clean_html(html_string)
```

#### HTML diff

Escape hatch — not wrapped.

```python
from lxml.html.diff import htmldiff, html_annotate
diff = htmldiff(old_html, new_html)
annotated = html_annotate([(html1, "v1"), (html2, "v2")])
```

---

### CSS Selectors

> `claw html select` wraps CSS selection for the common path — see [claw/html.md](claw/html.md). Requires `pip install cssselect` for the library API. `soup.select(...)` also works in BeautifulSoup without cssselect.

```python
from lxml.cssselect import CSSSelector
sel = CSSSelector("div.main > p.intro"); results = sel(root)
root.cssselect("div.main > p.intro")
```

Supported selectors: `*`, `tag`, `.class`, `#id`, `[attr]`, `[attr=val]`, `[attr~=val]`, `[attr|=val]`, `[attr^=val]`, `[attr$=val]`, `[attr*=val]`, `:first-child`, `:last-child`, `:nth-child()`, `:nth-last-child()`, `:nth-of-type()`, `:only-child`, `:only-of-type`, `:empty`, `:not()`, `>`, `+`, `~`, ` ` (descendant).

---

### Parsing Options

```python
parser = etree.XMLParser(
    encoding="utf-8",
    remove_blank_text=True,     # strip ignorable whitespace
    remove_comments=True,
    remove_pis=True,            # processing instructions
    strip_cdata=True,
    resolve_entities=True,
    no_network=True,
    recover=False,              # try to recover from errors
    huge_tree=False,            # allow very deep/large trees
)
tree = etree.parse("file.xml", parser)
html_parser = etree.HTMLParser(encoding="utf-8", remove_blank_text=True, remove_comments=True)
```

#### iterparse (streaming — covered by `claw xml stream-xpath`)

```python
for event, elem in etree.iterparse("large.xml", events=("start", "end"), tag="record"):
    if event == "end":
        process(elem)
        elem.clear()                                  # free memory
        while elem.getprevious() is not None:
            del elem.getparent()[0]
```

#### Feed parser / custom resolvers

```python
parser = etree.XMLParser()
parser.feed("<root>")
parser.feed("<child/>")
parser.feed("</root>")
root = parser.close()

class MyResolver(etree.Resolver):
    def resolve(self, system_url, public_id, context):
        return self.resolve_string("<fallback/>", context)
parser.resolvers.add(MyResolver())
```

---

### Namespace Handling

```python
nsmap = {"ns": "http://example.com/ns"}
root = etree.Element("{http://example.com/ns}root", nsmap=nsmap)
root.xpath("//ns:elem", namespaces=nsmap)
etree.QName("http://example.com/ns", "tag")        # Clark notation helper
etree.QName(elem).localname                         # strip namespace
etree.QName(elem).namespace
```

---

### Custom Element Classes

```python
class MyElement(etree.ElementBase):
    @property
    def name(self):
        return self.get("name")

lookup = etree.ElementNamespaceClassLookup()
lookup.get_namespace("http://example.com")["record"] = MyElement
parser = etree.XMLParser()
parser.set_element_class_lookup(lookup)
```

---

### objectify / ObjectPath

```python
from lxml import objectify
root = objectify.fromstring("<root><item>1</item><item>2</item></root>")
root.item                   # first <item>
root.item[1]                # second <item>
int(root.item)              # auto-type (int, float, bool, str)

path = objectify.ObjectPath("root.item")
path(root)
path.setattr(root, "new")
```

---

### Error Handling / Logging

```python
try:
    root = etree.fromstring(bad_xml)
except etree.XMLSyntaxError as e:
    for entry in e.error_log:
        print(entry.line, entry.column, entry.message)

log = etree.use_global_python_log(etree.PyErrorLog())   # global log capture
```

---

## BeautifulSoup4

```
pip install beautifulsoup4 lxml html5lib
```

```python
from bs4 import BeautifulSoup, Comment, SoupStrainer, UnicodeDammit
```

### Parsers

| Parser | Install | Speed | Lenient | Use when |
|--------|---------|-------|---------|----------|
| `html.parser` | built-in | moderate | moderate | No extra deps needed |
| `lxml` | `pip install lxml` | fast | yes | Speed matters, well-formed HTML |
| `html5lib` | `pip install html5lib` | slow | very | Must match browser parsing exactly |
| `lxml-xml` / `xml` | `pip install lxml` | fast | no | Parsing XML (not HTML) |

### Object Types

| Type | Description |
|------|-------------|
| `Tag` | HTML/XML element (`soup.div`) |
| `NavigableString` | Text within a tag |
| `BeautifulSoup` | Whole document |
| `Comment`, `CData`, `ProcessingInstruction`, `Declaration`, `Doctype` | Special text nodes |

### Navigation (down / up / sideways / parse order)

Down: `.contents`, `.children`, `.descendants`, `.string`, `.strings`, `.stripped_strings`.
Up: `.parent`, `.parents`.
Sideways: `.next_sibling`, `.previous_sibling`, `.next_siblings`, `.previous_siblings`.
Parse order: `.next_element`, `.previous_element`, `.next_elements`, `.previous_elements`.

### Search

> `claw html select` wraps all common `find` / `find_all` / CSS-select calls — see [claw/html.md](claw/html.md). Below: API surface for escape-hatch use (complex predicates, relative searches).

Core: `soup.find(tag, ...)` / `soup.find_all(tag, ...)` / `soup("div")` (shortcut).

Filter types: string (exact), regex (`re.compile(...)`), list (`["h1","h2"]`), `True` (any), predicate (`lambda tag: tag.has_attr("id")`).

Relative search methods: `find_parent(s)`, `find_next_sibling(s)`, `find_previous_sibling(s)`, `find_next`, `find_all_next`, `find_previous`, `find_all_previous`.

CSS selectors (no `cssselect` needed): `soup.select("div.main > p.intro")` · `soup.select_one(...)`. Same selector grammar as §CSS Selectors above.

### Tree modification

> `claw html unwrap | wrap | replace` cover common edits — see [claw/html.md](claw/html.md). Below: full API surface.

- Construct: `soup.new_tag("a", href="...", class_="link")`.
- Insert: `tag.append(child)` · `extend([c1, c2])` · `insert(pos, child)` · `insert_before(child)` · `insert_after(child)`.
- Remove: `tag.clear()` · `tag.extract()` (returns tag) · `tag.decompose()`.
- Replace / wrap: `tag.replace_with(new)` · `tag.wrap(soup.new_tag("div"))` · `tag.unwrap()`.
- Merge adjacent text: `tag.smooth()`.

### Output

> `claw html fmt` covers pretty-print — see [claw/html.md](claw/html.md).

`str(soup)` · `soup.prettify(formatter="html5")` · `tag.decode_contents()` / `tag.encode_contents()` (inner HTML) · `tag.get_text(separator=" ", strip=True)`.

Custom formatter (escape hatch):

```python
from bs4.formatter import HTMLFormatter
fmt = HTMLFormatter(indent=4, void_element_close_prefix=" /")
soup.prettify(formatter=fmt)
```

### Encoding

```python
dammit = UnicodeDammit(byte_string)
dammit.unicode_markup             # decoded string
dammit.original_encoding          # detected encoding
dammit = UnicodeDammit(byte_string, ["windows-1252", "iso-8859-1"])

soup = BeautifulSoup(html, "lxml", from_encoding="iso-8859-1")
soup = BeautifulSoup(html, "lxml", exclude_encodings=["ascii"])

fixed = UnicodeDammit.detwingle(byte_string)   # fix mixed UTF-8 + Windows-1252
```

### SoupStrainer (Partial Parsing)

Parse only matching elements — faster, less memory:

```python
only_links = SoupStrainer("a")
only_main = SoupStrainer(id="main")
custom = SoupStrainer(lambda name, attrs: name == "div" and "data-id" in attrs)
soup = BeautifulSoup(html, "lxml", parse_only=only_links)
```

### Multi-valued attributes

`class` is a list; `id` is a string. Disable via `BeautifulSoup(html, "lxml", multi_valued_attributes=None)`.

```python
tag["class"]                       # ["a", "b"]
soup.find_all("div", class_="a")   # matches if "a" in class list
```

### Attribute / tag access

```python
tag["href"]; tag.get("href", "default")
tag.attrs; tag["class"] = "new"; del tag["class"]
tag.has_attr("class")
tag.name; tag.name = "span"         # rename tag
```

---

## Escape-hatch recipes

These are the workflows `claw` doesn't wrap — they benefit from the full lxml / BeautifulSoup surface.

### 1. XSLT with parameters + access control (sandboxed)

```python
ac = etree.XSLTAccessControl(read_file=False, write_file=False, read_network=False)
transform = etree.XSLT(etree.parse("xform.xsl"), access_control=ac)
result = transform(
    etree.parse("in.xml"),
    year=etree.XSLT.strparam("2026"),
    author=etree.XSLT.strparam("Finance"),
)
open("out.xml", "wb").write(bytes(result))
print(transform.error_log)
```

### 2. Streaming huge XML with `iterparse` + memory cleanup

Never load a multi-GB invoice dump into memory — scan and clear:

```python
total = 0
for _, elem in etree.iterparse("big.xml", tag="invoice"):
    total += float(elem.findtext("amount") or 0)
    elem.clear()
    while elem.getprevious() is not None:
        del elem.getparent()[0]
```

### 3. Schematron business-rule validation

XSD checks structure; Schematron checks *rules* (e.g. "if type=shipment then tracking_id required"):

```python
sch = etree.Schematron(etree.parse("rules.sch"), store_report=True)
ok = sch.validate(etree.parse("invoice.xml"))
if not ok:
    for ent in sch.validation_report.iter("{http://purl.oclc.org/dsdl/svrl}failed-assert"):
        print(ent.get("location"), ent.findtext("{*}text").strip())
```

### 4. Custom `Resolver` for catalog-based DTD resolution

Prevents unwanted network fetches of external DTDs:

```python
class CatalogResolver(etree.Resolver):
    CATALOG = {"http://x.com/schema.dtd": "/opt/schemas/x.dtd"}
    def resolve(self, url, public_id, context):
        if url in self.CATALOG:
            return self.resolve_filename(self.CATALOG[url], context)
        return self.resolve_empty(context)

parser = etree.XMLParser(no_network=True, load_dtd=True)
parser.resolvers.add(CatalogResolver())
etree.parse("doc.xml", parser)
```

### 5. `SoupStrainer` + `UnicodeDammit` — salvage a broken legacy page

Scrape only `<a>` tags, auto-detecting the charset:

```python
raw = open("legacy.html", "rb").read()
ud = UnicodeDammit(raw, ["windows-1252", "iso-8859-1", "utf-8"])
soup = BeautifulSoup(ud.unicode_markup, "html.parser",
                    parse_only=SoupStrainer("a"))
hrefs = [a["href"] for a in soup.find_all("a", href=True)]
```
