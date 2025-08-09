DATABASE_URL ?= $(shell grep '^DATABASE_URL=' .env | cut -d '=' -f2-)
ALEMBIC_DIR = common/database/migrations
ALEMBIC_CMD = source venv/bin/activate && DATABASE_URL=$(DATABASE_URL) alembic -c alembic.ini

# Check if venv exists, if not create it and install requirements
venv-check:
	@test -d "venv" || ( \
		echo "🛠️  Creating virtual environment..." && \
		python3 -m venv venv && \
		source venv/bin/activate && \
		pip install -r requirements.txt \
	)

# Setup Playwright browsers
setup-playwright: venv-check
	@echo "🎭 Installing Playwright browsers..."
	@source venv/bin/activate && python install_playwright.py

# Complete setup including migrations and Playwright
setup: venv-check setup-playwright
	@echo "🚀 Complete setup finished!"

.PHONY: migrate upgrade downgrade venv-check setup-playwright setup seed seed-clear

# Create a new migration
migrate: venv-check
	@$(ALEMBIC_CMD) revision --autogenerate -m "$(name)"

# Upgrade DB
upgrade: venv-check
	@$(ALEMBIC_CMD) upgrade $(if $(target),$(target),head)

# Downgrade DB
downgrade: venv-check
	@$(ALEMBIC_CMD) downgrade $(if $(steps),$(steps),-1)

# Seed database with sample candidates
seed: venv-check
	@echo "🌱 Seeding database with sample candidates..."
	@source venv/bin/activate && DATABASE_URL=$(DATABASE_URL) python -m common.database.seeders

# Clear seeded candidates
seed-clear: venv-check
	@echo "🗑️  Clearing seeded candidates..."
	@source venv/bin/activate && DATABASE_URL=$(DATABASE_URL) python -m common.database.seeders --clear-only

serve: venv-check
	python main.py
