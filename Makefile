.PHONY: setup up down crawl dbt-run lint test

# Setup global environment and dependencies
setup:
	uv venv
	uv pip install -e .[dev]
	uv pip install pre-commit --system || true
	pre-commit install

# Start Local Infrastructure
up:
	docker compose up -d

# Stop Local Infrastructure
down:
	docker compose down

# Run the crawler
crawl:
	uv run python crawler/fetch_tiki.py

# Run dbt transformations
dbt-run:
	cd dbt_tiki && uv run dbt run

# Run linters
lint:
	uv run black crawler/
	uv run flake8 crawler/
	cd dbt_tiki && uv run sqlfluff lint models

# Run tests
test:
	uv run pytest crawler/tests/
