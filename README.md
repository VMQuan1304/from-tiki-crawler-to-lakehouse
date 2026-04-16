<div align="center">
  <h1>Tiki Lakehouse Project 🌊🛒</h1>
  <p><em>A modern open-source Data Pipeline & Lakehouse simulating E-Commerce operations</em></p>

  [![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)]()
  [![dbt](https://img.shields.io/badge/dbt-DuckDB-FF694B?logo=dbt&logoColor=white)]()
  [![Trino](https://img.shields.io/badge/Trino-Query_Engine-DD00A1?logo=trino&logoColor=white)]()
  [![MinIO](https://img.shields.io/badge/MinIO-S3_Storage-C7202C?logo=minio&logoColor=white)]()
</div>

---

## 🛠️ Tech Stack & Architecture

| Component | Technology | Description |
| :--- | :---: | :--- |
| **Ingestion Engine** | 🐍 Python | Custom crawlers scraping Tiki API using `requests` and converting structures to nested `Parquet`. |
| **Data Lake** | 🪣 MinIO | Self-hosted S3-compatible object storage defining our raw and consumption layers. |
| **Data Transformation** | 🔨 dbt + DuckDB | Compiles SQL transformations and materializes external Iceberg/Parquet tables directly in MinIO. |
| **Query Engine** | ⚡ Trino | Distributed SQL Query engine cataloged against MinIO via an Iceberg Postgres Metastore. |
| **Visualization BI** | 📊 Superset | Fast, interactive dashboarding interface mapping to Trino databases. |
| **Package Manager** | ☄️ uv | astral-sh/uv manages blazing fast virtual environments entirely in the project root. |

## 📂 Project Structure

```text
tiki-lakehouse/
├── .github/workflows/       # CI/CD Pipelines (Formatting & dbt linting)
├── crawler/
│   ├── tests/               # Pytest scripts (e.g., test_fetch.py)
│   └── fetch_tiki.py        # Extract & Load script fetching data to MinIO
├── dbt_tiki/                # dbt models, config, and schema rules
│   ├── models/              
│   ├── dbt_project.yml      
│   └── profiles.yml         # Configures DuckDB HTTPFS & S3 AWS extensions
├── trino/                   # Trino deployment files
│   └── etc/                 # Cluster & Iceberg Catalog properties
├── .env.example             # Template for API Keys & Passwords
├── .pre-commit-config.yaml  # Configured to standardize Python and SQL code
├── docker-compose.yml       # Local infrastructure setup (Trino, MinIO, Postgres, Superset)
├── Makefile                 # Shortcuts for `up`, `crawl`, `dbt-run`, `lint`
└── pyproject.toml           # Root package and tool configurations
```

## 🚀 Quick Start

### 1. Launch Infrastructure
Turn on the components using Docker Compose:
```bash
make up
```
*Access Ports:*
- **MinIO Console:** `http://localhost:9001` *(admin / minio_password)*
- **Trino UI:** `http://localhost:8080` *(admin)*
- **Apache Superset:** `http://localhost:8088` *(admin / admin_password)*

### 2. Prepare Environment
Instantiate the Python virtual environments with `uv` and setup pre-commit hooks:
```bash
cp .env.example .env
make setup
```

### 3. Extract & Load Data (Crawl)
Scrape new product arrays immediately into MinIO:
```bash
make crawl
```

### 4. Transform & Query
Utilize DuckDB to execute dbt transforms:
```bash
make dbt-run
```

---

_Managed professionally with standard SWE practices, GitHub Actions, and Pre-commit Hooks._
