"""Path, Theme, Recent, and Type views and the view check (#9), on rendered output."""

import posixpath
import re
import shutil
import subprocess

from conftest import REPO
from scripts.metadata import CONTENT_FOLDERS
from scripts.themes import load_themes
from scripts.view_check import check, listed, listings

LLM_MECHANICS = [  # the llm-mechanics samples, alphabetical by title
    "topics/sample-leading-tokenization.html",
    "dictionary/sample-token.html",
    "tools/sample-tool.html",
    "topics/sample-tokenization.html",
]


def test_dictionary_lists_its_terms(site):
    assert listed(site, "dictionary/index.html", "dictionary") == ["dictionary/sample-token.html"]


def test_topics_are_listed_newest_first(site):
    assert listed(site, "topics/index.html", "topics") == [
        "topics/sample-leading-tokenization.html",
        "topics/sample-tokenization.html",
    ]


def test_recent_shows_every_page_as_cards_newest_first(site):
    html = (site / "recent.html").read_text()
    assert "quarto-listing-container-grid" in html
    assert listed(site, "recent.html", "recent") == [
        "essays/sample-essay.html",
        "tools/sample-tool.html",
        "prototypes/sample-prototype.html",
        "topics/sample-leading-tokenization.html",
        "topics/sample-tokenization.html",
        "dictionary/sample-token.html",
    ]


def test_theme_page_lists_every_page_of_its_theme_any_type(site):
    assert listed(site, "themes/llm-mechanics.html", "theme") == LLM_MECHANICS
    assert listed(site, "themes/ai-assisted-engineering.html", "theme") == [
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


def test_view_check_is_the_last_step_of_make_check():
    dry_run = subprocess.run(
        ["make", "-n", "check"], cwd=REPO, capture_output=True, text=True, check=True
    )
    steps = re.search(r"for step in (.*?);", dry_run.stdout).group(1).split()
    assert steps[-1] == "check-views"
