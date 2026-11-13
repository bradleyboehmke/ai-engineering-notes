"""Validate content-page front matter against ADR-0001 and the themes data file.

Runs on source files, before render: an invalid page would otherwise just be
missing from the views. Every failure names the file and the rule broken, and
all failures are reported in one run.

    python -m scripts.metadata [ROOT]   # exits 1 on any failure
"""

import datetime
import sys
from pathlib import Path

import yaml

from scripts.themes import THEMES_FILE, load_themes

CONTENT_FOLDERS = ["topics", "dictionary", "essays", "prototypes", "tools"]
PAGE_SUFFIXES = {".qmd", ".md"}
# `date` is required because the Recent view sorts on it: Quarto lists an
# undated page as the newest, so a missing date would silently misorder it.
REQUIRED = ["title", "type", "theme", "maturity", "date"]
ALLOWED = {
    "type": ["topic", "term", "essay", "prototype", "tool"],
    "lens": ["practitioner", "leader"],  # absent means practitioner
    "maturity": ["seed", "draft", "solid"],
}


class FrontMatterError(Exception):
    pass


def content_pages(root: Path) -> list[Path]:
    """Pages in the content folders. A folder's `index` page is a view, not content."""
    pages = [
        p
        for folder in CONTENT_FOLDERS
        for p in (root / folder).rglob("*")
        if p.suffix in PAGE_SUFFIXES and p.stem != "index"
    ]
    return sorted(pages, key=lambda p: p.relative_to(root).as_posix())


def read_front_matter(path: Path) -> dict:
    lines = path.read_text().splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontMatterError("no YAML front matter found")
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        raise FrontMatterError("no YAML front matter found") from None
    try:
        meta = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as e:
        raise FrontMatterError(f"front matter is not valid YAML ({e})".replace("\n", " "))
    if not isinstance(meta, dict):
        raise FrontMatterError("front matter is not a YAML mapping")
    return meta


def check_stage(meta: dict, theme: str, expected: int | None) -> list[str]:
    """Stage is derived from theme: equal to it, or empty for stageless themes."""
    stage = meta.get("stage")
    if stage == "":
        stage = None
    if expected is None and stage is not None:
        return [f'stage {stage} is set but theme "{theme}" has no stage']
    if expected is not None and stage is None:
        return [f'stage is empty but theme "{theme}" has stage {expected}']
    if stage != expected:
        return [f'stage {stage} does not match theme "{theme}" (stage {expected})']
    return []


def page_date(meta: dict) -> datetime.date | None:
    """The page's `date` as a calendar date, or None if it isn't one."""
    value = meta.get("date")
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def check_page(meta: dict, stages: dict[str, int | None]) -> list[str]:
    """Rules broken by one page's front matter, in a stable order."""
    errors = [f'required field "{f}" is missing' for f in REQUIRED if f not in meta]
    for field, allowed in ALLOWED.items():
        if field in meta and meta[field] not in allowed:
            errors.append(f'{field} "{meta[field]}" is not one of: {", ".join(allowed)}')
    if "theme" in meta:
        theme = meta["theme"]
        if theme in stages:
            errors += check_stage(meta, theme, stages[theme])
        else:
            errors.append(f'theme "{theme}" is not a known theme slug (see data/themes.yml)')
    if "prereqs" in meta and not isinstance(meta["prereqs"], list):
        errors.append("prereqs must be a list")
    if "date" in meta and page_date(meta) is None:
        errors.append("date must be a YYYY-MM-DD date")
    if "video" in meta and not isinstance(meta["video"], str):
        errors.append("video must be a string")
    return errors


def validate(root: Path, themes_file: Path = THEMES_FILE) -> list[str]:
    """Return every failure as `<path relative to root>: <rule broken>`."""
    stages = {t.slug: t.stage for t in load_themes(themes_file)}
    errors = []
    for path in content_pages(root):
        rel = path.relative_to(root).as_posix()
        try:
            problems = check_page(read_front_matter(path), stages)
        except FrontMatterError as e:
            problems = [str(e)]
        errors += [f"{rel}: {p}" for p in problems]
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    errors = validate(root)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"metadata validation: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print(f"metadata validation: {len(content_pages(root))} page(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
