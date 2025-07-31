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

.PHONY: migrate upgrade downgrade venv-check

# Create a new migration
migrate: venv-check
	@$(ALEMBIC_CMD) revision --autogenerate -m "$(name)"

# Upgrade DB
upgrade: venv-check
	@$(ALEMBIC_CMD) upgrade $(if $(target),$(target),head)

# Downgrade DB
downgrade: venv-check
	@$(ALEMBIC_CMD) downgrade $(if $(steps),$(steps),-1)

test: venv-check
	python main.py "$(prompt)"
