"""Sample pages and the shared page layout (#7), asserted on rendered output."""

import posixpath
import re
import shutil
import subprocess
from html import unescape as html_unescape

from conftest import REPO, quarto_env


def page(site, rel: str) -> str:
    return (site / rel).read_text()


def page_meta(html: str) -> str:
    """The shared metadata block the layout puts at the top of every content page."""
    match = re.search(r'<div class="page-meta">(.*?)</div>', html, re.S)
    assert match, "page has no page-meta block"
    return match.group(1)


def test_topic_shows_theme_display_name_and_maturity(site):
    meta = page_meta(page(site, "topics/sample-tokenization.html"))
    assert "LLM mechanics for builders" in meta
    assert "seed" in meta


def prereq_hrefs(meta: str) -> dict[str, str]:
    """Map each prereq slug in a page-meta block to the href it links to."""
    links = {}
    for tag in re.findall(r"<a\b[^>]*>", meta):
        slug = re.search(r'data-prereq="([^"]+)"', tag)
        if slug:
            links[slug.group(1)] = re.search(r'href="([^"]+)"', tag).group(1)
    return links


def resolve(rel: str, href: str) -> str:
    """Site-relative path that `href`, found on page `rel`, points to."""
    return posixpath.normpath(posixpath.join(posixpath.dirname(rel), href))


def test_topic_prereq_links_to_the_term_page(site):
    rel = "topics/sample-tokenization.html"
    links = prereq_hrefs(page_meta(page(site, rel)))
    assert {s: resolve(rel, h) for s, h in links.items()} == {
        "sample-token": "dictionary/sample-token.html"
    }
    assert (site / "dictionary" / "sample-token.html").exists()


def test_term_page_has_the_term_structure(site):
    html = page(site, "dictionary/sample-token.html")
    html = html[html.index('<main class="content"'):]  # skip the table of contents
    headings = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<h2[^>]*>(.*?)</h2>", html)]
    assert headings == ["Definition", "Related terms", "What to avoid", "Usage example"]


def content(html: str) -> str:
    """The page body, without navbar, table of contents, or footer."""
    return html[html.index('<main class="content"'):html.index("</main>")]


def test_topic_ends_with_leading_this_linking_the_leader_page(site):
    rel = "topics/sample-tokenization.html"
    body = content(page(site, rel))
    last_section = body[body.rindex("<h2"):]
    assert "Leading this" in last_section
    hrefs = {resolve(rel, h) for h in re.findall(r'href="([^"#]+)"', last_section)}
    assert "topics/sample-leading-tokenization.html" in hrefs


def test_leader_page_is_marked_and_topic_page_is_not(site):
    leader = page_meta(page(site, "topics/sample-leading-tokenization.html"))
    assert "Leader page" in leader
    assert "Leader page" not in page_meta(page(site, "topics/sample-tokenization.html"))


def test_leader_page_lists_the_topic_as_prereq(site):
    rel = "topics/sample-leading-tokenization.html"
    links = prereq_hrefs(page_meta(page(site, rel)))
    assert {s: resolve(rel, h) for s, h in links.items()} == {
        "sample-tokenization": "topics/sample-tokenization.html"
    }


SAMPLES = [
    "topics/sample-tokenization.html",
    "topics/sample-leading-tokenization.html",
    "dictionary/sample-token.html",
    "essays/sample-essay.html",
    "prototypes/sample-prototype.html",
    "tools/sample-tool.html",
]


def test_essay_embeds_its_video(site):
    html = content(page(site, "essays/sample-essay.html"))
    video = re.search(r'<div class="page-video[^"]*">\s*<iframe[^>]*src="([^"]+)"', html)
    assert video and video.group(1) == "https://www.youtube.com/embed/zjkBMFhNj_g"


def test_pages_without_video_have_no_embed(site):
    assert 'class="page-video' not in page(site, "topics/sample-tokenization.html")


def test_every_sample_is_a_seed(site):
    for rel in SAMPLES:
        assert 'data-maturity="seed"' in page_meta(page(site, rel)), rel


def test_samples_cover_two_staged_themes_and_one_stageless(site):
    themes = {
        re.search(r'data-theme="([^"]+)"', page_meta(page(site, rel))).group(1)
        for rel in SAMPLES
    }
    staged = {"llm-mechanics", "model-apis", "evals", "context-and-retrieval",
              "agents", "production"}
    stageless = {"ai-assisted-engineering", "leading-teams"}
    assert len(themes & staged) >= 2
    assert len(themes & stageless) >= 1


TOPIC_OUTPUT = "7 tokens: ['Models', 'read', 'text', 'as', 'tokens,', 'not', 'words.']"


def test_topic_code_output_is_rendered(site):
    assert html_unescape(content(page(site, "topics/sample-tokenization.html"))).count(
        TOPIC_OUTPUT
    ) == 1


def test_topic_rerenders_from_frozen_output_without_python(site, tmp_path):
    """With no working Python, the topic still renders its output from _freeze/."""
    copy = tmp_path / "repo"
    shutil.copytree(
        REPO, copy, ignore=shutil.ignore_patterns(".git", ".venv", "_site", ".quarto")
    )
    env = {**quarto_env(), "QUARTO_PYTHON": str(tmp_path / "no-such-python")}
    subprocess.run(["quarto", "render"], cwd=copy, check=True, env=env)
    html = (copy / "_site" / "topics" / "sample-tokenization.html").read_text()
    assert TOPIC_OUTPUT in html_unescape(html)


def test_staged_theme_shows_its_stage(site):
    meta = page_meta(page(site, "topics/sample-tokenization.html"))
    assert "(Stage 1)" in meta
    assert "Stage" not in page_meta(page(site, "essays/sample-essay.html"))
