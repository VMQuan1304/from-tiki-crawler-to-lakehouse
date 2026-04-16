<div align="center">
  <img src="https://img.icons8.com/?size=100&id=D0S250gH4vY2&format=png&color=000000" alt="Lakehouse Logo" width="100"/>
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
| **Ingestion Engine** | <img src="https://img.icons8.com/?size=100&id=13441&format=png&color=000000" width="24" /> Python | Custom crawlers scraping Tiki API using `requests` and converting structures to nested `Parquet`. |
| **Data Lake** | <img src="https://img.icons8.com/?size=100&id=tNl5qT02vXo5&format=png&color=000000" width="24" /> MinIO | Self-hosted S3-compatible object storage defining our raw and consumption layers. |
| **Data Transformation** | <img src="https://img.icons8.com/?size=100&id=tJ2_pI5P3JTo&format=png&color=000000" width="24" /> dbt + DuckDB | Compiles SQL transformations and materializes external Iceberg/Parquet tables directly in MinIO. |
| **Query Engine** | <img src="https://img.icons8.com/?size=100&id=jXyInXG-Xb-b&format=png&color=000000" width="24" /> Trino | Distributed SQL Query engine cataloged against MinIO via an Iceberg Postgres Metastore. |
| **Visualization BI** | <img src="https://img.icons8.com/?size=100&id=90558&format=png&color=000000" width="24" /> Superset | Fast, interactive dashboarding interface mapping to Trino databases. |
| **Package Manager** | <img src="https://img.icons8.com/?size=100&id=YbaO731-z8zX&format=png&color=000000" width="24" /> uv | astral-sh/uv manages blazing fast virtual environments entirely in the project root. |

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
