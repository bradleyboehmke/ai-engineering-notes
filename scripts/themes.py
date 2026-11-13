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
    """Return the themes in path order (staged by stage, then unstaged)."""
    entries = yaml.safe_load(path.read_text())
    return [Theme(e["slug"], e["title"], e.get("stage")) for e in entries]
