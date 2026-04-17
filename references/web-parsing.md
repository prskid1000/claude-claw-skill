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

```python
tree = etree.parse("file.xml")                       # from file
tree = etree.parse(StringIO(xml_string))              # from string IO
root = etree.fromstring(xml_bytes)                    # from bytes -> Element
root = etree.XML("<root><child/></root>")             # from string literal
doc  = etree.ElementTree(root)                        # wrap Element in tree
```

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

#### E-factory (declarative construction)

```python
from lxml.builder import E
html = E.html(E.head(E.title("Page")),
              E.body(E.p("Paragraph", {"class": "intro"})))
```

#### Serialize

```python
etree.tostring(root, pretty_print=True, encoding="unicode")
etree.tostring(root, method="html", encoding="utf-8")        # bytes
etree.tostring(root, xml_declaration=True, encoding="UTF-8")
etree.indent(root, space="  ")                                # in-place indent
tree.write("out.xml", pretty_print=True, xml_declaration=True, encoding="UTF-8")
etree.tostring(root, method="c14n")                           # C14N canonical
etree.tostring(root, method="c14n2")                          # C14N 2.0
```

---

### XPath 1.0

```python
root.xpath("//div")                               # all div elements
root.xpath("//div[@class='main']")                # attribute filter
root.xpath("//div/p/text()")                      # text content
root.xpath("//a/@href")                           # attribute values
root.xpath("count(//p)")                          # count (returns float)
root.xpath("//p[position()>2]")                   # positional
root.xpath("//p[last()]")                         # last element
root.xpath("//div[contains(@class,'item')]")      # contains
root.xpath("//div[starts-with(@id,'sec')]")       # starts-with
root.xpath("//h1 | //h2 | //h3")                 # union
root.xpath("//div[not(@hidden)]")                 # negation
root.xpath("normalize-space(//title)")            # normalize whitespace
root.xpath("string(//title)")                     # string value
```

XPath axes: `self`, `child`, `parent`, `ancestor`, `ancestor-or-self`, `descendant`, `descendant-or-self`, `following`, `following-sibling`, `preceding`, `preceding-sibling`, `attribute`, `namespace`.

#### Compiled / parameterized XPath

```python
find = etree.XPath("//div[@class=$cls]")
results = find(root, cls="main")                  # parameterized
evaluator = etree.XPathEvaluator(root)
find = etree.ETXPath("//{http://ns.example.com}tag")  # namespace-aware
```

#### EXSLT extensions

Supported namespaces: `regexp`, `set`, `math`, `string`, `date`.

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

> Use `claw xml validate` for XSD. RelaxNG, Schematron, and DTD stay in the library.

#### XML Schema (XSD) — covered by `claw xml validate`

```python
schema = etree.XMLSchema(etree.parse("schema.xsd"))
schema.validate(doc)                  # returns bool
schema.assertValid(doc)               # raises on invalid
schema.error_log                      # validation errors
parser = etree.XMLParser(schema=schema)   # validate during parse
```

#### RelaxNG

```python
rng = etree.RelaxNG(etree.parse("schema.rng"))
rng.validate(doc)
rng.error_log
# Compact syntax:
rng = etree.RelaxNG.from_rnc_string("element root { text }")
```

#### Schematron

```python
schematron = etree.Schematron(etree.parse("rules.sch"))
schematron.validate(doc)
report = schematron.validation_report     # SVRL XML report
```

#### DTD

```python
dtd = etree.DTD("schema.dtd")
dtd.validate(doc)
dtd.error_log
```

---

### lxml.html

```python
import lxml.html
doc = lxml.html.fromstring(html_string)
doc = lxml.html.parse("http://example.com")        # URL or file
doc = lxml.html.document_fromstring(html_string)    # full document
doc = lxml.html.fragment_fromstring(html_string)    # fragment
elements = lxml.html.fragments_fromstring(html_str) # multiple fragments
```

#### Element methods

```python
elem.text_content()        # all text (recursive)
elem.drop_tree()           # remove element and children
elem.drop_tag()            # remove tag, keep children/text
elem.classes                # set of CSS classes
elem.base_url              # resolved base URL
```

#### Links (covered by `claw html absolutize` / `claw html rewrite`)

```python
doc.make_links_absolute("http://base.url/")
doc.resolve_base_href()
for element, attribute, link, pos in doc.iterlinks():
    pass
doc.rewrite_links(lambda href: href.replace("old", "new"))
```

#### Forms

```python
for form in doc.forms:
    print(form.action, form.method, form.fields)
    form.fields["input_name"] = "value"
```

#### Cleaner (covered by `claw html sanitize`)

> Requires `pip install lxml_html_clean` (separated out of lxml in 5.2+). Alternatively `pip install 'lxml[html_clean]'`.

```python
from lxml_html_clean import Cleaner        # lxml 5.2+
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

```python
from lxml.html.diff import htmldiff, html_annotate
diff = htmldiff(old_html, new_html)
annotated = html_annotate([(html1, "v1"), (html2, "v2")])
```

---

### CSS Selectors

> Requires `pip install cssselect`. For simple cases `claw html select` and BeautifulSoup's `soup.select(...)` both work without this dep.

```python
from lxml.cssselect import CSSSelector
sel = CSSSelector("div.main > p.intro")
results = sel(root)
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

### Search (covered by `claw html select`)

```python
soup.find("div"); soup.find_all("div")
soup.find("div", class_="main"); soup.find("div", id="content")
soup.find("div", attrs={"data-id": "5"})
soup.find_all(["h1", "h2", "h3"])
soup.find_all(True)                           # all tags
soup.find_all(string=re.compile("pattern"))   # regex on text
soup("div")                                   # shortcut for find_all
```

Filter types: string (exact), regex, list, `True` (any), function predicate (`lambda tag: tag.has_attr("id")`).

Relative search: `find_parent(s)`, `find_next_sibling(s)`, `find_previous_sibling(s)`, `find_next`, `find_all_next`, `find_previous`, `find_all_previous`.

CSS selectors: `soup.select("div.main > p.intro")`, `soup.select_one(...)`, supports `[attr]`, `:nth-of-type()`, `h1, h2, h3`, etc.

### Tree modification

```python
new_tag = soup.new_tag("a", href="http://example.com", class_="link")
tag.append(new_tag); tag.extend([t1, t2]); tag.insert(0, new_tag)
tag.insert_before(new_tag); tag.insert_after(new_tag)
tag.clear(); tag.extract(); tag.decompose()
tag.replace_with(new_tag); tag.wrap(soup.new_tag("div")); tag.unwrap()
tag.smooth()                        # merge adjacent NavigableStrings
```

### Output

```python
str(soup)                           # full HTML
soup.prettify()                     # indented
soup.prettify(formatter="html5")    # HTML5 void elements
tag.decode_contents()               # inner HTML string
tag.encode_contents()               # inner HTML bytes
tag.get_text(separator=" ", strip=True)
```

Custom formatter:

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
