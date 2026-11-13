"""View check: each rendered view lists the expected pages in the expected order.

Runs on the rendered site (`_site/`), after render. Expectations come from
source front matter and `data/themes.yml`, never from listing config, so the
check stays valid however the views are built. Every failure names the view
page and the listing.

    python -m scripts.view_check [ROOT]   # reads ROOT/_site; exits 1 on any failure
"""

import datetime
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from scripts.metadata import FrontMatterError, content_pages, page_date, read_front_matter
from scripts.page_types import PageType, load_types
from scripts.themes import THEMES_FILE, Theme, load_themes, path_order

# A listing's container div; Quarto writes its `id` and `class` in either order.
CONTAINER = re.compile(
    r'<div (?=[^>]*\bclass="quarto-listing )[^>]*\bid="listing-([^"]+)"[^>]*>'
)


def listings(site: Path, view: str) -> dict[str, list[str]]:
    """Every listing on rendered view page `view`, in page order.

    Maps listing id to the site-relative pages it links to, in listed order.
    """
    html = (site / view).read_text()
    found = list(CONTAINER.finditer(html))
    result = {}
    for i, match in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(html)
        items = re.split(r"\bdata-index=", html[match.end() : end])[1:]
        hrefs = [re.search(r'href="([^"]+)"', item).group(1) for item in items]
        result[match.group(1)] = [
            posixpath.normpath(posixpath.join(posixpath.dirname(view), h)) for h in hrefs
        ]
    return result


# What each view should list, derived from source metadata.


@dataclass(frozen=True)
class Page:
    html: str  # site-relative output path
    title: str
    type: str | None
    theme: str | None
    date: datetime.date | None


def source_pages(root: Path) -> list[Page]:
    """Content pages with readable front matter (metadata validation flags the rest)."""
    pages = []
    for path in content_pages(root):
        try:
            meta = read_front_matter(path)
        except FrontMatterError:
            continue
        html = path.relative_to(root).with_suffix(".html").as_posix()
        title = str(meta.get("title", ""))
        pages.append(Page(html, title, meta.get("type"), meta.get("theme"), page_date(meta)))
    return pages


def by_title(pages: list[Page]) -> list[str]:
    return [p.html for p in sorted(pages, key=lambda p: p.title.casefold())]


def newest_first(pages: list[Page]) -> list[str]:
    def key(p: Page):
        return (-(p.date.toordinal() if p.date else 0), p.title.casefold())

    return [p.html for p in sorted(pages, key=key)]


RECENT_ITEMS = 10  # recent.qmd `max-items`: Recent shows only the newest pages

SORTS = {"title": by_title, "newest": newest_first}  # data/types.yml `sort` values


def expected_views(
    pages: list[Page], themes: list[Theme], types: list[PageType]
) -> list[tuple[str, str, list[str]]]:
    """Every (view page, listing id, expected pages in order)."""
    views = []
    for t in types:  # each Type view is its folder's index page, listing id = folder
        of_type = [p for p in pages if p.type == t.type]
        views.append((f"{t.folder}/index.html", t.folder, SORTS[t.sort](of_type)))
    views.append(("recent.html", "recent", newest_first(pages)[:RECENT_ITEMS]))
    of_theme = {t.slug: by_title([p for p in pages if p.theme == t.slug]) for t in themes}
    views += [(f"themes/{t.slug}.html", "theme", of_theme[t.slug]) for t in themes]
    views += [("path.html", f"path-{t.slug}", of_theme[t.slug]) for t in themes]
    return views


def compare(view: str, listing: str, expected: list[str], got: list[str]) -> list[str]:
    where = f'{view}: listing "{listing}"'
    errors = [f"{where} is missing {p}" for p in expected if p not in got]
    errors += [f"{where} lists unexpected {p}" for p in got if p not in expected]
    if not errors and got != expected:
        errors.append(
            f"{where} is out of order: expected {', '.join(expected)}; got {', '.join(got)}"
        )
    return errors


def check_path_order(rendered: dict[str, list[str]], themes: list[Theme]) -> list[str]:
    """The Path view's theme sections appear in path order (by stage, stageless last)."""
    wanted = [f"path-{t.slug}" for t in path_order(themes)]
    got = [i for i in rendered if i in wanted]
    expected = [i for i in wanted if i in got]
    if got != expected:
        return [
            "path.html: theme sections are out of path order: "
            f"expected {', '.join(expected)}; got {', '.join(got)}"
        ]
    return []


def check(root: Path, site: Path, themes_file: Path = THEMES_FILE) -> list[str]:
    """Return every failure as `<view page>: <problem>`."""
    themes = load_themes(themes_file)
    errors: list[str] = []
    rendered: dict[str, dict[str, list[str]] | None] = {}
    for view, listing, expected in expected_views(source_pages(root), themes, load_types()):
        if view not in rendered:
            rendered[view] = listings(site, view) if (site / view).exists() else None
            if rendered[view] is None:
                errors.append(f"{view}: view page not found")
        found = rendered[view]
        if found is None:
            continue
        if listing not in found:
            errors.append(f'{view}: listing "{listing}" not found')
            continue
        errors += compare(view, listing, expected, found[listing])
    if rendered.get("path.html"):
        errors += check_path_order(rendered["path.html"], themes)
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    errors = check(root, root / "_site")
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"view check: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print("view check: every view lists the expected pages in order")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
