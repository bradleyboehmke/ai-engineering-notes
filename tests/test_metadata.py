"""Metadata validation on source front matter (#6), rules from ADR-0001."""

import datetime
import subprocess
from pathlib import Path

import pytest
import yaml

from conftest import REPO
from scripts.metadata import validate

VALID = {
    "title": "LLM-as-judge evaluators",
    "type": "topic",
    "theme": "evals",
    "stage": 3,
    "maturity": "seed",
    "date": datetime.date(2026, 11, 13),
}


def write_page(root: Path, rel: str, meta: dict | None = None, raw: str | None = None) -> None:
    """Write a content page whose front matter is `meta` (as YAML) or `raw` text."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if raw is None:
        raw = "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n\nBody.\n"
    path.write_text(raw)


def test_valid_page_passes(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", VALID)
    assert validate(tmp_path) == []


def without(key: str) -> dict:
    return {k: v for k, v in VALID.items() if k != key}


@pytest.mark.parametrize("field", ["title", "type", "theme", "maturity", "date"])
def test_missing_required_field_fails(tmp_path, field):
    write_page(tmp_path, "topics/judge.qmd", without(field))
    assert validate(tmp_path) == [
        f'topics/judge.qmd: required field "{field}" is missing'
    ]


def test_bad_type_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "type": "article"})
    assert validate(tmp_path) == [
        'topics/judge.qmd: type "article" is not one of: topic, term, essay, prototype, tool'
    ]


def test_bad_lens_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "lens": "manager"})
    assert validate(tmp_path) == [
        'topics/judge.qmd: lens "manager" is not one of: practitioner, leader'
    ]


@pytest.mark.parametrize("lens", ["practitioner", "leader"])
def test_allowed_lens_passes(tmp_path, lens):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "lens": lens})
    assert validate(tmp_path) == []


def test_bad_maturity_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "maturity": "done"})
    assert validate(tmp_path) == [
        'topics/judge.qmd: maturity "done" is not one of: seed, draft, solid'
    ]


def test_bad_theme_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "theme": "eval"})
    assert validate(tmp_path) == [
        'topics/judge.qmd: theme "eval" is not a known theme slug (see data/themes.yml)'
    ]


def test_stage_that_disagrees_with_theme_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "stage": 2})
    assert validate(tmp_path) == [
        'topics/judge.qmd: stage 2 does not match theme "evals" (stage 3)'
    ]


def test_missing_stage_on_a_staged_theme_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", without("stage"))
    assert validate(tmp_path) == [
        'topics/judge.qmd: stage is empty but theme "evals" has stage 3'
    ]


def test_stage_set_on_a_stageless_theme_fails(tmp_path):
    meta = {**VALID, "theme": "leading-teams", "stage": 7}
    write_page(tmp_path, "topics/judge.qmd", meta)
    assert validate(tmp_path) == [
        'topics/judge.qmd: stage 7 is set but theme "leading-teams" has no stage'
    ]


@pytest.mark.parametrize("empty", ["absent", None, ""])
def test_empty_stage_on_a_stageless_theme_passes(tmp_path, empty):
    meta = {**without("stage"), "theme": "ai-assisted-engineering"}
    if empty != "absent":
        meta["stage"] = empty
    write_page(tmp_path, "essays/assist.qmd", meta)
    assert validate(tmp_path) == []


def test_prereqs_that_is_not_a_list_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "prereqs": "eval-datasets"})
    assert validate(tmp_path) == ["topics/judge.qmd: prereqs must be a list"]


def test_video_that_is_not_a_string_fails(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "video": 42})
    assert validate(tmp_path) == ["topics/judge.qmd: video must be a string"]


@pytest.mark.parametrize("date", ["2026-11-31", "last week", 20261113])
def test_date_that_is_not_a_calendar_date_fails(tmp_path, date):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "date": date})
    assert validate(tmp_path) == ["topics/judge.qmd: date must be a YYYY-MM-DD date"]


def test_optional_fields_of_the_right_shape_pass(tmp_path):
    meta = {**VALID, "prereqs": ["eval-datasets"], "video": "https://youtu.be/x"}
    write_page(tmp_path, "topics/judge.qmd", meta)
    assert validate(tmp_path) == []


def test_every_failure_is_reported_in_one_run(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**without("title"), "maturity": "done"})
    write_page(tmp_path, "dictionary/token.md", {**VALID, "type": "term", "theme": "x"})
    assert validate(tmp_path) == [
        'dictionary/token.md: theme "x" is not a known theme slug (see data/themes.yml)',
        'topics/judge.qmd: required field "title" is missing',
        'topics/judge.qmd: maturity "done" is not one of: seed, draft, solid',
    ]


def test_pages_outside_content_folders_are_not_validated(tmp_path):
    for rel in ["learning/evals/lesson.qmd", "notes/n.md", "index.qmd"]:
        write_page(tmp_path, rel, {"title": "Not content"})
    assert validate(tmp_path) == []


def test_folder_index_pages_are_views_not_content(tmp_path):
    write_page(tmp_path, "dictionary/index.qmd", {"title": "Dictionary", "listing": {}})
    assert validate(tmp_path) == []


def test_page_without_front_matter_fails(tmp_path):
    write_page(tmp_path, "essays/bare.qmd", raw="# Just a heading\n")
    assert validate(tmp_path) == ["essays/bare.qmd: no YAML front matter found"]


def test_page_with_invalid_yaml_fails(tmp_path):
    write_page(tmp_path, "essays/bad.qmd", raw="---\ntitle: [unclosed\n---\n\nBody.\n")
    [error] = validate(tmp_path)
    assert error.startswith("essays/bad.qmd: front matter is not valid YAML")


def run_check(root: Path) -> subprocess.CompletedProcess:
    """Run the check step as `make check` does."""
    return subprocess.run(
        ["make", "--no-print-directory", "check-metadata", f"ROOT={root}"],
        cwd=REPO, capture_output=True, text=True,
    )


def test_check_step_fails_and_names_file_and_rule(tmp_path):
    write_page(tmp_path, "topics/judge.qmd", {**VALID, "theme": "eval"})
    result = run_check(tmp_path)
    assert result.returncode != 0
    assert 'topics/judge.qmd: theme "eval" is not a known theme slug' in result.stderr


def test_check_step_passes_on_the_real_repo():
    result = run_check(REPO)
    assert result.returncode == 0, result.stderr


def test_check_is_part_of_make_check():
    dry_run = subprocess.run(
        ["make", "-n", "check"], cwd=REPO, capture_output=True, text=True, check=True
    )
    assert "check-metadata" in dry_run.stdout


def test_themes_come_only_from_the_themes_data_file(tmp_path):
    themes = tmp_path / "themes.yml"
    themes.write_text("- slug: robotics\n  title: Robotics\n  stage: 9\n")
    write_page(tmp_path, "topics/arm.qmd", {**VALID, "theme": "robotics", "stage": 9})
    write_page(tmp_path, "topics/judge.qmd", VALID)
    assert validate(tmp_path, themes_file=themes) == [
        'topics/judge.qmd: theme "evals" is not a known theme slug (see data/themes.yml)'
    ]
