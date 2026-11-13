"""Read the single source for page types and their folders, `data/types.yml`."""

from dataclasses import dataclass
from pathlib import Path

import yaml

TYPES_FILE = Path(__file__).resolve().parent.parent / "data" / "types.yml"


@dataclass(frozen=True)
class PageType:
    type: str  # the `type` value in page front matter
    folder: str  # content folder; its `index` page is the Type view
    title: str  # Type view title
    sort: str  # Type view order: "newest" or "title"


def load_types(path: Path = TYPES_FILE) -> list[PageType]:
    """Return the page types in file order (the Browse menu order)."""
    entries = yaml.safe_load(path.read_text())
    return [PageType(e["type"], e["folder"], e["title"], e["sort"]) for e in entries]


CONTENT_FOLDERS = [t.folder for t in load_types()]
