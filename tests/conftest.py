"""Shared fixtures. Tests run against the rendered site (the one seam)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def quarto_env() -> dict[str, str]:
    """Environment for running Quarto with this interpreter (the pinned .venv)."""
    return {**os.environ, "QUARTO_PYTHON": sys.executable}


@pytest.fixture(scope="session")
def site() -> Path:
    """Render the site once per test session and return the `_site/` path."""
    subprocess.run(["quarto", "render"], cwd=REPO, check=True, env=quarto_env())
    return REPO / "_site"
