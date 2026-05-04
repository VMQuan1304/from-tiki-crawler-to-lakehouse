# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

All Python commands use `uv run` to pick up the project's virtual environment.

```bash
# Environment setup
make setup          # Create venv and install all dependencies (uv pip install -e .[dev])

# Infrastructure
make up             # Start Docker services (MinIO, Postgres, Trino, Superset)
make down           # Stop Docker services

# Pipeline
make crawl          # Run the Tiki crawler (writes Parquet to MinIO raw-data bucket)
make dbt-run        # Run dbt transformations (cd dbt_tiki && uv run dbt run)

# Linting
make lint           # Black + Flake8 on crawler/, SQLFluff on dbt_tiki/models/

# Testing
make test                              # Run all crawler tests
uv run pytest crawler/tests/test_fetch.py  # Run a single test file

# Airflow (standalone, not in Docker)
make airflow-start  # Exports AIRFLOW_HOME=./airflow_home, port 8081
```

## Architecture Overview

This is a **Modern Data Stack Lakehouse** that processes Tiki.vn product data through Bronze → Silver → Gold layers.

### Data Flow

```
Tiki API → crawler/fetch_tiki.py → MinIO (s3://raw-data/tiki_products/*.parquet)
                                          ↓
                               dbt + DuckDB (runs locally, NOT in Docker)
                                          ↓
                           MinIO (s3://raw-data/marts/fct_tiki_books.parquet)
                                          ↓
                    Trino (iceberg catalog) ← Superset dashboards
```

The DAG in `dags/tiki_lakehouse_dag.py` orchestrates: `crawl → dbt run → analytics_plot.py`.

### Key Architectural Decisions

**dbt runs outside Docker**: `dbt_tiki/profiles.yml` connects DuckDB directly to MinIO via `httpfs` extension (S3 endpoint: `localhost:9000`). Trino is not used as the dbt target — DuckDB handles all transformations.

**Trino uses JDBC-backed Iceberg catalog**: `trino/etc/catalog/iceberg.properties` stores Iceberg metadata in Postgres (not Hive Metastore). The default warehouse is `s3://lakehouse/`, separate from the raw bucket `s3://raw-data/`.

**Nested data flattening**: The crawler (`crawler/fetch_tiki.py`) converts all dict/list columns to strings via `.astype(str)` before writing Parquet. dbt's staging model then uses `REGEXP_EXTRACT` to parse values back out (e.g., `quantity_sold` from a stringified dict).

**dbt materialization**: Staging models are `view` (DuckDB in-memory). Marts are `external` Parquet files written back to MinIO at `s3://raw-data/marts/`.

### Service URLs (defaults from `.env.example`)

| Service | URL | Credentials |
|---|---|---|
| MinIO Console | `http://localhost:9001` | `admin` / `minio_password` |
| Trino UI | `http://localhost:8080` | `admin` |
| Superset | `http://localhost:8088` | `admin` / `admin_password` |
| Airflow | `http://localhost:8081` | standalone, check terminal |

### Environment Variables

Copy `.env.example` to `.env` before running. The crawler reads `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` from the environment (defaults fall back to `localhost:9000` / `admin` / `minio_password`).

### Coding Philosophy

Do not over-engineer. Keep source code and pytest tests as simple as possible.

### Linting Rules

- Python: Black with `line-length = 100`, Flake8 ignoring `E203`
- SQL: SQLFluff with `duckdb` dialect (configured in `dbt_tiki/.sqlfluff`)
- Pre-commit hooks enforce all of the above plus trailing whitespace and YAML checks