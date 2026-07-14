# ---------------------------------------------------------------------------
# Course entry points.
#
# A Makefile is the "front door" of a repository: it documents, in runnable
# form, everything a human or a CI server needs to do here. Module 2 discusses
# why this matters; Module 6 shows CI calling these exact targets.
# ---------------------------------------------------------------------------

PYTHON  ?= python3
MODULE  ?=

.PHONY: help setup data lint test check solutions clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Create a virtualenv and install the course tooling
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"
	@echo ""
	@echo "Done. Activate with:  source .venv/bin/activate"

data: ## Generate the synthetic CoreCafé source data (data/raw/)
	$(PYTHON) -m datagen --output data/raw --days 30

lint: ## Lint and check formatting (ruff)
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

check: ## Check YOUR exercise solutions for one module, e.g.: make check MODULE=03
ifeq ($(strip $(MODULE)),)
	@echo "Usage: make check MODULE=03   (use the two-digit module number)"; exit 1
endif
	COURSE_TARGET=exercises $(PYTHON) -m pytest modules/$(MODULE)-*/tests -q

test: ## Run the full course test suite against the reference solutions (used by CI)
	COURSE_TARGET=solutions $(PYTHON) -m pytest -q

solutions: ## Same as 'make check' but runs the reference solutions, e.g.: make solutions MODULE=03
ifeq ($(strip $(MODULE)),)
	@echo "Usage: make solutions MODULE=03"; exit 1
endif
	COURSE_TARGET=solutions $(PYTHON) -m pytest modules/$(MODULE)-*/tests -q

clean: ## Remove generated data and caches
	rm -rf data .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
