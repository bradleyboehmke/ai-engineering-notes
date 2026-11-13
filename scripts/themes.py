"""Read the single source for themes, `data/themes.yml`."""

from dataclasses import dataclass
from pathlib import Path

import yaml

THEMES_FILE = Path(__file__).resolve().parent.parent / "data" / "themes.yml"


@dataclass(frozen=True)
class Theme:
    slug: str
    title: str
    stage: int | None  # None for themes without a stage


def load_themes(path: Path = THEMES_FILE) -> list[Theme]:
    """Return the themes in file order."""
    entries = yaml.safe_load(path.read_text())
    return [Theme(e["slug"], e["title"], e.get("stage")) for e in entries]


def path_order(themes: list[Theme]) -> list[Theme]:
    """Themes in path order: by stage, then stageless themes; file order breaks ties.

    scripts/site_data.lua orders the Path view the same way.
    """
    return sorted(themes, key=lambda t: (t.stage is None, t.stage or 0))
