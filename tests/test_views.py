"""Path, Theme, Recent, and Type views and the view check (#9), on rendered output."""

import posixpath
import re
import shutil
import subprocess

import pytest

from conftest import REPO
from scripts.page_types import CONTENT_FOLDERS
from scripts.themes import load_themes
from scripts.view_check import check, listings
from test_site_skeleton import render_copy_with

LLM_MECHANICS = [  # the llm-mechanics samples, alphabetical by title
    "topics/sample-leading-tokenization.html",
    "dictionary/sample-token.html",
    "tools/sample-tool.html",
    "topics/sample-tokenization.html",
]


def test_dictionary_lists_its_terms(site):
    assert listings(site, "dictionary/index.html")["dictionary"] == ["dictionary/sample-token.html"]


def test_topics_are_listed_newest_first(site):
    assert listings(site, "topics/index.html")["topics"] == [
        "topics/sample-leading-tokenization.html",
        "topics/sample-tokenization.html",
    ]


def test_recent_shows_pages_as_cards_newest_first(site):
    html = (site / "recent.html").read_text()
    assert "quarto-listing-container-grid" in html
    assert listings(site, "recent.html")["recent"] == [
        "essays/sample-essay.html",
        "tools/sample-tool.html",
        "prototypes/sample-prototype.html",
        "topics/sample-leading-tokenization.html",
        "topics/sample-tokenization.html",
        "dictionary/sample-token.html",
    ]


def test_type_views_never_show_a_raw_theme_slug(site):
    """A listing can't map a slug to its display name, so Type views drop the column."""
    for folder in CONTENT_FOLDERS:
        html = (site / folder / "index.html").read_text()
        main = html[html.index('<main class="content"'):html.index("</main>")]
        cells = {c.strip() for c in re.findall(r">([^<>]+)<", main)}
        assert not cells & {t.slug for t in load_themes()}, folder


def test_theme_page_lists_every_page_of_its_theme_any_type(site):
    assert listings(site, "themes/llm-mechanics.html")["theme"] == LLM_MECHANICS
    assert listings(site, "themes/ai-assisted-engineering.html")["theme"] == [
        "essays/sample-essay.html"
    ]


def test_every_theme_has_a_theme_page(site):
    for theme in load_themes():
        assert "theme" in listings(site, f"themes/{theme.slug}.html"), theme.slug


def test_path_groups_by_theme_in_path_order_with_stageless_last(site):
    groups = listings(site, "path.html")
    assert list(groups) == [
        "path-llm-mechanics",
        "path-model-apis",
        "path-evals",
        "path-context-and-retrieval",
        "path-agents",
        "path-production",
        "path-ai-assisted-engineering",
        "path-leading-teams",
    ]
    assert groups["path-llm-mechanics"] == LLM_MECHANICS
    assert groups["path-model-apis"] == ["prototypes/sample-prototype.html"]
    assert groups["path-evals"] == []
    assert groups["path-ai-assisted-engineering"] == ["essays/sample-essay.html"]


# The view check: expectations from source metadata, asserted on _site/.


def tampered_site(site, tmp_path, view: str, old: str, new: str):
    """A copy of the rendered site with one edit made to one view page."""
    copy = tmp_path / "_site"
    shutil.copytree(site, copy)
    html = (copy / view).read_text()
    assert old in html
    (copy / view).write_text(html.replace(old, new, 1))
    return copy


def source_copy(tmp_path, extra: dict[str, str] | None = None):
    """A copy of the content folders, with extra source pages added."""
    root = tmp_path / "repo"
    for folder in CONTENT_FOLDERS:
        shutil.copytree(REPO / folder, root / folder)
    for rel, text in (extra or {}).items():
        (root / rel).write_text(text)
    return root


def test_view_check_passes_on_the_rendered_site(site):
    assert check(REPO, site) == []


def test_view_check_fails_when_a_view_lists_pages_in_the_wrong_order(site, tmp_path):
    leader, topic = "../topics/sample-leading-tokenization.html", "../topics/sample-tokenization.html"
    swapped = tampered_site(site, tmp_path, "topics/index.html", leader, "SWAP")
    html = (swapped / "topics/index.html").read_text()
    html = html.replace(topic, leader).replace("SWAP", topic)
    (swapped / "topics/index.html").write_text(html)
    assert check(REPO, swapped) == [
        'topics/index.html: listing "topics" is out of order: expected '
        "topics/sample-leading-tokenization.html, topics/sample-tokenization.html; got "
        "topics/sample-tokenization.html, topics/sample-leading-tokenization.html"
    ]


def test_view_check_fails_when_a_view_lists_the_wrong_page(site, tmp_path):
    wrong = tampered_site(
        site, tmp_path, "dictionary/index.html",
        'href="../dictionary/sample-token.html"', 'href="../tools/sample-tool.html"',
    )
    assert check(REPO, wrong) == [
        'dictionary/index.html: listing "dictionary" is missing dictionary/sample-token.html',
        'dictionary/index.html: listing "dictionary" lists unexpected tools/sample-tool.html',
    ]


def test_view_check_fails_when_a_page_is_missing_from_the_views(site, tmp_path):
    page = (
        "---\ntitle: Unrendered\ntype: essay\ntheme: evals\nstage: 3\n"
        "maturity: seed\ndate: 2026-11-12\n---\n\nBody.\n"
    )
    root = source_copy(tmp_path, {"essays/unrendered.qmd": page})
    missing = "is missing essays/unrendered.html"
    assert check(root, site) == [
        f'essays/index.html: listing "essays" {missing}',
        f'recent.html: listing "recent" {missing}',
        f'themes/evals.html: listing "theme" {missing}',
        f'path.html: listing "path-evals" {missing}',
    ]


def test_view_check_fails_when_path_groups_are_out_of_order(site, tmp_path):
    renamed = tampered_site(
        site, tmp_path, "path.html", 'id="listing-path-evals"', 'id="listing-path-evals-x"'
    )
    errors = check(REPO, renamed)
    assert 'path.html: listing "path-evals" not found' in errors


def test_view_check_fails_when_a_view_page_is_missing(site, tmp_path):
    copy = tmp_path / "_site"
    shutil.copytree(site, copy)
    (copy / "themes" / "agents.html").unlink()
    assert check(REPO, copy) == ["themes/agents.html: view page not found"]


def run_check(root):
    return subprocess.run(
        ["make", "--no-print-directory", "check-views", f"ROOT={root}"],
        cwd=REPO, capture_output=True, text=True,
    )


def test_check_step_fails_and_names_the_view(site, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    shutil.copytree(source_copy(tmp_path), root, dirs_exist_ok=True)
    tampered = tampered_site(
        site, tmp_path, "dictionary/index.html",
        'href="../dictionary/sample-token.html"', 'href="../tools/sample-tool.html"',
    )
    shutil.move(tampered, root / "_site")
    result = run_check(root)
    assert result.returncode != 0
    assert 'dictionary/index.html: listing "dictionary" is missing' in result.stderr


VIEW_PAGES = ["path.html", "themes/index.html", "recent.html"] + [
    f"{folder}/index.html" for folder in CONTENT_FOLDERS
]


def test_every_view_is_in_the_navbar(site):
    html = (site / "index.html").read_text()
    navbar = html[html.index('<nav class="navbar'):html.index("</nav>")]
    hrefs = {h.removeprefix("./") for h in re.findall(r'href="([^"]+)"', navbar)}
    assert set(VIEW_PAGES) <= hrefs


def test_themes_index_links_every_theme_page(site):
    html = (site / "themes/index.html").read_text()
    content = html[html.index('<main class="content"'):]
    targets = {posixpath.normpath(f"themes/{h}") for h in re.findall(r'href="([^"#]+)"', content)}
    assert {f"themes/{t.slug}.html" for t in load_themes()} <= targets


def test_start_here_points_at_the_path_and_recent_views(site):
    html = (site / "index.html").read_text()
    content = html[html.index('<main class="content"'):]
    assert 'href="./path.html"' in content
    assert 'href="./recent.html"' in content


# A variant repo: themes.yml out of stage order, and more pages than Recent shows.

REORDERED_THEMES = """\
- slug: leading-teams
  title: Leading AI engineering teams
  stage:
- slug: evals
  title: Evals
  stage: 3
- slug: production
  title: Production
  stage: 6
- slug: llm-mechanics
  title: LLM mechanics for builders
  stage: 1
- slug: ai-assisted-engineering
  title: AI-assisted engineering
  stage:
- slug: agents
  title: Agents
  stage: 5
- slug: model-apis
  title: Building with model APIs
  stage: 2
- slug: context-and-retrieval
  title: Context engineering and retrieval
  stage: 4
"""

NEWER = {  # six pages newer than every sample: 12 content pages in all
    f"essays/newer-{d}.qmd": (
        f"---\ntitle: Newer {d}\ntype: essay\ntheme: evals\nstage: 3\n"
        f"maturity: seed\ndate: 2026-12-0{d}\n---\n\nBody.\n"
    )
    for d in range(1, 7)
}


@pytest.fixture(scope="module")
def variant(tmp_path_factory):
    """(root, rendered _site/) of the variant repo."""
    files = {"data/themes.yml": REORDERED_THEMES, **NEWER}
    site = render_copy_with(tmp_path_factory.mktemp("variant"), files)
    return site.parent, site


def test_path_orders_themes_by_stage_not_file_order(variant):
    _, site = variant
    assert list(listings(site, "path.html")) == [
        "path-llm-mechanics",
        "path-model-apis",
        "path-evals",
        "path-context-and-retrieval",
        "path-agents",
        "path-production",
        "path-leading-teams",  # stageless last, in file order
        "path-ai-assisted-engineering",
    ]


def test_start_here_orders_themes_by_stage_not_file_order(variant):
    _, site = variant
    index = (site / "index.html").read_text()
    assert re.findall(r'<span class="listing-title">(.*?)</span>', index) == [
        "LLM mechanics for builders",
        "Building with model APIs",
        "Evals",
        "Context engineering and retrieval",
        "Agents",
        "Production",
        "Leading AI engineering teams",
        "AI-assisted engineering",
    ]


def test_recent_shows_only_the_newest_ten(variant):
    _, site = variant
    assert listings(site, "recent.html")["recent"] == [
        "essays/newer-6.html",
        "essays/newer-5.html",
        "essays/newer-4.html",
        "essays/newer-3.html",
        "essays/newer-2.html",
        "essays/newer-1.html",
        "essays/sample-essay.html",
        "tools/sample-tool.html",
        "prototypes/sample-prototype.html",
        "topics/sample-leading-tokenization.html",
    ]


def test_view_check_passes_on_the_variant(variant):
    root, site = variant
    assert check(root, site, themes_file=root / "data/themes.yml") == []


def test_view_check_orders_stageless_themes_by_file_order(site, tmp_path):
    """Swapping the two stageless themes in the data file changes the expected Path."""
    themes = tmp_path / "themes.yml"
    themes.write_text(REORDERED_THEMES)
    staged = (
        "path-llm-mechanics, path-model-apis, path-evals, "
        "path-context-and-retrieval, path-agents, path-production"
    )
    assert check(REPO, site, themes_file=themes) == [
        f"path.html: theme sections are out of path order: expected {staged}, "
        f"path-leading-teams, path-ai-assisted-engineering; got {staged}, "
        "path-ai-assisted-engineering, path-leading-teams"
    ]


def test_view_check_expects_recent_to_drop_pages_older_than_the_newest_ten(site, tmp_path):
    root = source_copy(tmp_path, NEWER)  # the real site has rendered none of NEWER
    recent = [e for e in check(root, site) if e.startswith("recent.html")]
    assert recent == [
        f'recent.html: listing "recent" is missing essays/newer-{d}.html' for d in range(6, 0, -1)
    ] + [
        'recent.html: listing "recent" lists unexpected topics/sample-tokenization.html',
        'recent.html: listing "recent" lists unexpected dictionary/sample-token.html',
    ]


def test_view_check_is_the_last_step_of_make_check():
    dry_run = subprocess.run(
        ["make", "-n", "check"], cwd=REPO, capture_output=True, text=True, check=True
    )
    steps = re.search(r"for step in (.*?);", dry_run.stdout).group(1).split()
    assert steps[-1] == "check-views"
