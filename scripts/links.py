"""Check internal links in the rendered site (`_site/`).

Runs after render, on every HTML page that exists, so new pages (views
included) are covered without changes here. External links are not checked.
Every failure names the source page and the broken target, and all failures
are reported in one run.

    python -m scripts.links [SITE]   # default _site; exits 1 on any failure
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


# Quarto renders a cross-reference it cannot resolve as <strong>?@ref</strong>.
UNRESOLVED_XREF = re.compile(r"^\?(@[\w:.-]+)$")


class PageParser(HTMLParser):
    """Collect link targets, element ids, and unresolved xrefs in one HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        # (target, prereq slug or None): prereq links come from the page-layout
        # filter as <a class="prereq" data-prereq="<slug>">.
        self.targets: list[tuple[str, str | None]] = []
        self.ids: set[str] = set()
        self.unresolved: list[str] = []
        self._in_strong = False

    def handle_endtag(self, tag):
        if tag == "strong":
            self._in_strong = False

    def handle_data(self, data):
        if self._in_strong and (m := UNRESOLVED_XREF.match(data.strip())):
            self.unresolved.append(m.group(1))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "strong":
            self._in_strong = True
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        prereq = a.get("data-prereq") if tag == "a" else None
        for key in ("href", "src"):
            if a.get(key):
                self.targets.append((a[key], prereq))


def is_external(target: str) -> bool:
    parts = urlsplit(target)
    return bool(parts.scheme or parts.netloc)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(errors="replace"))
    return parser


def resolve(site: Path, page: Path, path: str) -> Path | None:
    """The file in `site` that a link's path part points at, or None."""
    file = (page.parent / unquote(path)).resolve()
    if file.is_dir():
        file = file / "index.html"
    if not file.is_file() or not file.is_relative_to(site.resolve()):
        return None
    return file


def check_links(site: Path) -> list[str]:
    parsed: dict[Path, PageParser] = {}

    def page_parser(path: Path) -> PageParser:
        if path not in parsed:
            parsed[path] = parse(path)
        return parsed[path]

    failures = []
    for page in sorted(site.rglob("*.html")):
        rel = page.relative_to(site).as_posix()
        for ref in page_parser(page.resolve()).unresolved:
            failures.append(f'{rel}: cross-reference "{ref}" is unresolved')
        for target, prereq in page_parser(page.resolve()).targets:
            if is_external(target):
                continue
            parts = urlsplit(target)
            file = resolve(site, page, parts.path) if parts.path else page.resolve()
            if file is None:
                if prereq:
                    failures.append(f'{rel}: prereq "{prereq}" names no page')
                else:
                    failures.append(f'{rel}: link "{target}" resolves to no file')
                continue
            anchor = unquote(parts.fragment)
            if anchor and file.suffix == ".html" and anchor not in page_parser(file).ids:
                failures.append(f'{rel}: link "{target}" has no target id "{anchor}"')
    return failures


def main(argv: list[str]) -> int:
    site = Path(argv[1]) if len(argv) > 1 else Path("_site")
    if not site.is_dir():
        print(f"links: {site}/ not found; render the site first", file=sys.stderr)
        return 1
    failures = check_links(site)
    for f in failures:
        print(f, file=sys.stderr)
    if failures:
        print(f"links: {len(failures)} broken link(s)", file=sys.stderr)
        return 1
    print("links: all internal links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
