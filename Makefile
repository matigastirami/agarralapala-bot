DATABASE_URL ?= $(shell grep '^DATABASE_URL=' .env | cut -d '=' -f2-)

# Tell the Makefile when we’re inside Docker (set in Dockerfile)
IN_DOCKER ?= 0

# Commands abstracted for local vs docker
ifeq ($(IN_DOCKER),1)
  ACTIVATE :=
  PY := python
  PIP := pip
else
  ACTIVATE := source venv/bin/activate &&
  PY := venv/bin/python
  PIP := venv/bin/pip
endif

ALEMBIC_DIR = common/database/migrations
ALEMBIC_CMD = $(ACTIVATE) DATABASE_URL=$(DATABASE_URL) $(PY) -m alembic -c alembic.ini

# Only create a venv locally
venv-check:
ifeq ($(IN_DOCKER),1)
	@echo "🐳 Skipping venv inside Docker"
else
	@test -d "venv" || ( \
		echo "🛠️  Creating virtual environment..." && \
		python3 -m venv venv && \
		$(ACTIVATE) $(PIP) install -r requirements.txt \
	)
endif

# Setup Playwright browsers
setup-playwright: venv-check
	@echo "🎭 Installing Playwright browsers..."
	@$(ACTIVATE) $(PY) install_playwright.py

# Complete setup including migrations and Playwright
setup: venv-check setup-playwright
	@echo "🚀 Complete setup finished!"

.PHONY: migrate upgrade downgrade venv-check setup-playwright setup seed seed-clear

migrate: venv-check
	@$(ALEMBIC_CMD) revision --autogenerate -m "$(name)"

upgrade: venv-check
	@$(ALEMBIC_CMD) upgrade $(if $(target),$(target),head)

downgrade: venv-check
	@$(ALEMBIC_CMD) downgrade $(if $(steps),$(steps),-1)

seed: venv-check
	@echo "🌱 Seeding database with sample candidates..."
	@$(ACTIVATE) DATABASE_URL=$(DATABASE_URL) $(PY) -m common.database.seeders

seed-clear: venv-check
	@echo "🗑️  Clearing seeded candidates..."
	@$(ACTIVATE) DATABASE_URL=$(DATABASE_URL) $(PY) -m common.database.seeders --clear-only

serve: venv-check
	$(PY) main.py

# Testing targets
test-enrichment: venv-check
	@echo "🧪 Testing job enrichment workflow..."
	@$(ACTIVATE) $(PY) test_job_enrichment.py

test-enrichment-cron: venv-check
	@echo "🧪 Testing job enrichment cron..."
	@$(ACTIVATE) $(PY) crons/job_enrichment_cron.py

debug-workflow: venv-check
	@echo "🔍 Debugging workflow step by step..."
	@$(ACTIVATE) $(PY) debug_workflow.py

# Quick test all
test-all: test-enrichment test-enrichment-cron debug-workflow
	@echo "✅ All tests completed!"
