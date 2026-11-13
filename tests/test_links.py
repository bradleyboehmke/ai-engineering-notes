"""Internal link and prereq checker (#8), run against the rendered site."""

import re
import subprocess

import pytest

from conftest import REPO
from scripts.links import check_links
from test_site_skeleton import render_copy_with

PAGE = "---\ntitle: {title}\ntype: topic\ntheme: evals\nstage: 3\nmaturity: seed\n{extra}---\n\n{body}\n"


def page(title: str, body: str = "Body.", extra: str = "") -> str:
    return PAGE.format(title=title, body=body, extra=extra)


# One deliberately broken page per rule, rendered once into a copy of the repo.
FIXTURES = {
    "topics/bad-link.qmd": page("Bad link", "See [gone](no-such-page.qmd)."),
    "topics/bad-anchor.qmd": page(
        "Bad anchor",
        "## Here {#here}\n\n[Fine](#here), [off page](sample-tokenization.qmd#nowhere),"
        " [on page](#missing).",
    ),
    "topics/bad-xref.qmd": page("Bad xref", "As @fig-nothing shows."),
    "topics/external.qmd": page(
        "External", "[Off site](https://example.invalid/missing.html#nope)."
    ),
    "topics/bad-prereq.qmd": page(
        "Bad prereq", extra="prereqs: [sample-tokenization, no-such-prereq]\n"
    ),
    # Prereqs resolve like metadata validation: any content page, subfolders
    # included; never a folder index view; never a slug two pages share.
    "essays/deeper/nested-page.qmd": page("Nested page"),
    "topics/nested-prereq.qmd": page("Nested prereq", extra="prereqs: [nested-page]\n"),
    "topics/index-prereq.qmd": page("Index prereq", extra="prereqs: [index]\n"),
    "topics/dup.qmd": page("Dup topic"),
    "tools/dup.qmd": page("Dup tool"),
    "topics/dup-prereq.qmd": page("Dup prereq", extra="prereqs: [dup]\n"),
}


@pytest.fixture(scope="module")
def broken_site(tmp_path_factory):
    return render_copy_with(tmp_path_factory.mktemp("links"), FIXTURES)


@pytest.fixture(scope="module")
def failures(broken_site):
    return check_links(broken_site)


def test_broken_internal_link_fails(failures):
    assert 'topics/bad-link.html: link "no-such-page.qmd" resolves to no file' in failures


def test_link_to_missing_anchor_on_another_page_fails(failures):
    assert (
        'topics/bad-anchor.html: link "../topics/sample-tokenization.html#nowhere"'
        ' has no target id "nowhere"'
    ) in failures


def test_link_to_missing_anchor_on_same_page_fails(failures):
    assert 'topics/bad-anchor.html: link "#missing" has no target id "missing"' in failures


def test_link_to_existing_anchor_passes(failures):
    assert not any('"#here"' in f for f in failures)


def test_unresolved_cross_reference_fails(failures):
    assert 'topics/bad-xref.html: cross-reference "@fig-nothing" is unresolved' in failures


def test_prereq_naming_a_missing_page_fails(failures):
    prereq_failures = [f for f in failures if f.startswith("topics/bad-prereq.html")]
    assert prereq_failures == [
        'topics/bad-prereq.html: prereq "no-such-prereq" names no page'
    ]


def test_prereq_in_a_subfolder_links_to_it(broken_site, failures):
    html = (broken_site / "topics/nested-prereq.html").read_text()
    assert 'href="../essays/deeper/nested-page.html"' in html
    assert not any(f.startswith("topics/nested-prereq.html") for f in failures)


def test_prereq_naming_a_folder_index_view_fails(failures):
    assert 'topics/index-prereq.html: prereq "index" names no page' in failures


def test_prereq_naming_a_slug_two_pages_share_fails(failures):
    assert 'topics/dup-prereq.html: prereq "dup" names no page' in failures


def test_external_links_are_ignored(failures):
    assert not any(f.startswith("topics/external.html") for f in failures)


def test_each_broken_fixture_is_the_only_failure(failures):
    """The rest of the site (samples, views, nav) has no broken links."""
    broken = {"bad-link", "bad-anchor", "bad-xref", "bad-prereq", "index-prereq", "dup-prereq"}
    assert {f.split(":")[0] for f in failures} == {f"topics/{b}.html" for b in broken}


def test_real_rendered_site_passes(site):
    assert check_links(site) == []


def test_make_check_runs_link_check_and_fails_on_broken_link(broken_site):
    """The check step, run as `make check` does, fails and names page and target."""
    result = subprocess.run(
        ["make", "--no-print-directory", "check-links", f"ROOT={broken_site.parent}"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert 'topics/bad-link.html: link "no-such-page.qmd" resolves to no file' in result.stderr


def test_make_check_validates_metadata_before_render_then_checks_links_and_views():
    dry_run = subprocess.run(
        ["make", "-n", "check"], cwd=REPO, capture_output=True, text=True, check=True
    )
    steps = re.search(r"for step in (.*?);", dry_run.stdout).group(1).split()
    assert steps == ["check-metadata", "render", "check-links", "check-views"]
