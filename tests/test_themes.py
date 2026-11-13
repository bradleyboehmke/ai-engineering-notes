"""The themes data file is the single source for the theme list (#5)."""

from scripts.themes import load_themes

# Independent source of truth: the slugs and stages in ROADMAP.md.
ROADMAP_STAGES = {
    "llm-mechanics": 1,
    "model-apis": 2,
    "evals": 3,
    "context-and-retrieval": 4,
    "agents": 5,
    "production": 6,
    "ai-assisted-engineering": None,
    "leading-teams": None,
}


def test_themes_are_exactly_the_roadmap_slugs_with_their_stages():
    themes = load_themes()
    assert {t.slug: t.stage for t in themes} == ROADMAP_STAGES


def test_themes_are_in_path_order_with_unstaged_last():
    assert [t.slug for t in load_themes()] == list(ROADMAP_STAGES)


def test_every_theme_has_a_display_name():
    assert all(t.title.strip() for t in load_themes())
