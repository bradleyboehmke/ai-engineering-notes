# AI Engineering Notes: local commands. CI runs `make check` and `make test`.
#
#   make preview   live local preview while writing
#   make render    render the site into _site/
#   make check     render, then run every check step (what CI runs)
#   make test      run the tests for the check scripts (tests/)
#
# Python comes from a local .venv built from requirements.txt. Quarto runs
# page code with that interpreter via QUARTO_PYTHON.

VENV   := .venv
PYTHON := $(VENV)/bin/python
QUARTO := QUARTO_PYTHON=$(abspath $(PYTHON)) quarto

# Check steps, run in this order by `make check`. To add one, write
# scripts/<name>.py (exits non-zero and names the file and rule on failure),
# add a `check-<name>` target below, and append it here. Planned order:
# render -> link check -> metadata validation -> view check. Metadata
# validation reads source front matter, so it does not depend on render.
CHECK_STEPS := render
CHECK_STEPS += check-links
CHECK_STEPS += check-metadata
CHECK_STEPS += check-views

# Root the check steps run against (tests point it at temp-dir fixtures).
ROOT := .

.PHONY: preview render check test venv clean check-links check-metadata check-views

$(PYTHON): requirements.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --quiet --upgrade pip
	$(PYTHON) -m pip install --quiet -r requirements.txt
	@touch $(PYTHON)

venv: $(PYTHON)

preview: $(PYTHON)
	$(QUARTO) preview

render: $(PYTHON)
	$(QUARTO) render

check:
	@for step in $(CHECK_STEPS); do \
	  $(MAKE) --no-print-directory $$step || exit 1; \
	done
	@echo "check: all steps passed ($(CHECK_STEPS))"

# Internal links, anchors, cross-references, and prereqs in the rendered
# site ($(ROOT)/_site). External links are not checked.
check-links: $(PYTHON)
	$(PYTHON) -m scripts.links $(ROOT)/_site

# Metadata validation on source front matter (ADR-0001 + data/themes.yml).
check-metadata: $(PYTHON)
	$(PYTHON) -m scripts.metadata $(ROOT)

# View check on the rendered site: each view lists the expected pages, in order.
check-views: $(PYTHON)
	$(PYTHON) -m scripts.view_check $(ROOT)

test: $(PYTHON)
	$(PYTHON) -m pytest

clean:
	rm -rf _site .quarto
