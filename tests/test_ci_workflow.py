"""Structural guarantees of the CI workflow (#10).

GitHub Actions can't run locally, so these assert the workflow's contract:
the check runs everywhere, and only a passing main build is deployed.
"""

import re

import yaml

from conftest import REPO

WORKFLOW = REPO / ".github" / "workflows" / "site.yml"
QUARTO_VERSION = "1.11.9"


def load():
    data = yaml.safe_load(WORKFLOW.read_text())
    # YAML 1.1 reads the bare key `on` as boolean True.
    data["on"] = data.pop(True, data.get("on"))
    return data


def steps(job):
    return load()["jobs"][job]["steps"]


def runs(job):
    return [s.get("run", "") for s in steps(job)]


def uses(job):
    return [s["uses"] for s in steps(job) if "uses" in s]


def test_check_runs_on_every_push_and_pull_request():
    triggers = load()["on"]
    assert "push" in triggers and "pull_request" in triggers
    for event in ("push", "pull_request"):
        assert not (triggers[event] or {}).get("branches"), f"{event} is branch-filtered"


def test_check_installs_exactly_the_pinned_quarto():
    setup = [s for s in steps("check") if s.get("uses", "").startswith("quarto-dev/quarto-actions/setup@")]
    assert len(setup) == 1
    assert str(setup[0]["with"]["version"]) == QUARTO_VERSION


def test_check_runs_make_check_and_make_test():
    commands = runs("check")
    assert "make check" in commands
    assert "make test" in commands


def test_check_uploads_the_site_for_deploy():
    assert any(u.startswith("actions/upload-pages-artifact@") for u in uses("check"))


def test_deploy_needs_check_and_runs_only_on_main_pushes():
    deploy = load()["jobs"]["deploy"]
    assert deploy["needs"] in ("check", ["check"])
    condition = deploy["if"]
    assert "github.ref == 'refs/heads/main'" in condition
    assert "github.event_name == 'push'" in condition


def test_deploy_publishes_to_pages_with_least_privilege():
    deploy = load()["jobs"]["deploy"]
    assert deploy["permissions"] == {"pages": "write", "id-token": "write"}
    assert deploy["environment"]["name"] == "github-pages"
    assert any(u.startswith("actions/deploy-pages@") for u in uses("deploy"))


def test_actions_are_pinned_to_a_major_version():
    for job in load()["jobs"]:
        for ref in uses(job):
            assert re.search(r"@v\d+(\.\d+)*$", ref), f"{job}: {ref} is not version-pinned"
