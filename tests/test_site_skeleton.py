"""Acceptance checks for the site skeleton (#5), asserted on rendered output."""

import re
import shutil
import subprocess

from conftest import REPO, quarto_env
from scripts.themes import load_themes

META_DOCS = ["README", "MISSION", "ROADMAP", "GLOSSARY", "CLAUDE", "LICENSE", "LICENSE-CODE"]
WORKING_FOLDERS = ["learning", "notes", "inbox", "docs"]
CONTENT_FOLDERS = ["topics", "dictionary", "essays", "prototypes", "tools"]


def test_start_here_is_the_landing_page(site):
    index = (site / "index.html").read_text()
    assert "<title>Start Here – AI Engineering Notes</title>" in index


def test_start_here_lists_every_theme_in_path_order(site):
    index = (site / "index.html").read_text()
    listed = re.findall(r'<span class="listing-title">(.*?)</span>', index)
    assert listed == [t.title for t in load_themes()]


def test_meta_docs_are_not_published(site):
    published = {p.stem for p in site.rglob("*") if p.is_file()}
    assert published.isdisjoint(META_DOCS)


def render_copy_with(tmp_path, pages: dict[str, str]):
    """Render a copy of the repo with extra pages added; return its `_site/`."""
    copy = tmp_path / "repo"
    shutil.copytree(
        REPO, copy, ignore=shutil.ignore_patterns(".git", ".venv", "_site", ".quarto")
    )
    for rel, text in pages.items():
        (copy / rel).parent.mkdir(parents=True, exist_ok=True)
        (copy / rel).write_text(text)
    subprocess.run(["quarto", "render"], cwd=copy, check=True, env=quarto_env())
    return copy / "_site"


def test_only_content_folders_are_published(tmp_path):
    """Render with a probe page in every folder; only content folders publish."""
    probe = "---\ntitle: Probe\n---\n\nProbe.\n"
    out = render_copy_with(
        tmp_path, {f"{f}/probe.md": probe for f in CONTENT_FOLDERS + WORKING_FOLDERS}
    )
    for folder in CONTENT_FOLDERS:
        assert (out / folder / "probe.html").exists(), f"{folder}/ was not rendered"
    for folder in WORKING_FOLDERS:
        assert not (out / folder).exists(), f"{folder}/ was published"


LICENSE_URL = "https://github.com/bradleyboehmke/ai-engineering-notes/blob/main/LICENSE"


def test_footer_states_both_licenses(site):
    index = (site / "index.html").read_text()
    footer = index[index.index('<footer class="footer">'):]
    assert "CC BY 4.0" in footer and f'href="{LICENSE_URL}"' in footer
    assert "MIT" in footer and f'href="{LICENSE_URL}-CODE"' in footer


def test_search_indexes_start_here(site):
    import json

    index = (site / "index.html").read_text()
    assert 'id="quarto-search"' in index
    entries = json.loads((site / "search.json").read_text())
    assert any(e["title"] == "Start Here" for e in entries)


def test_python_code_in_a_page_executes(tmp_path):
    page = "---\ntitle: Code\n---\n\n```{python}\nprint(6 * 7)\n```\n"
    out = render_copy_with(tmp_path, {"topics/code.qmd": page})
    assert "42" in (out / "topics" / "code.html").read_text()
