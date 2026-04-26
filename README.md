<div align="center">
  <h1>Tiki Lakehouse Project 🌊🛒</h1>
  <p><em>A modern open-source Data Pipeline & Lakehouse simulating E-Commerce operations</em></p>

  [![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)]()
  [![dbt](https://img.shields.io/badge/dbt-DuckDB-FF694B?logo=dbt&logoColor=white)]()
  [![Trino](https://img.shields.io/badge/Trino-Query_Engine-DD00A1?logo=trino&logoColor=white)]()
  [![MinIO](https://img.shields.io/badge/MinIO-S3_Storage-C7202C?logo=minio&logoColor=white)]()
  [![Airflow](https://img.shields.io/badge/Airflow-Orchestration-017CEE?logo=apache-airflow&logoColor=white)]()
</div>

---

## 📖 Project Overview

This project implements a **Modern Data Stack (MDS)** Lakehouse architecture to crawl, store, transform, and visualize product data from [Tiki.vn](https://tiki.vn). It demonstrates how to build a scalable data platform using open-source tools like **MinIO**, **Trino**, **Apache Iceberg**, and **dbt**.

### Key Features
- **Automated Ingestion**: Custom Python crawler fetching Tiki API data and storing it in MinIO (S3-compatible).
- **Lakehouse Architecture**: Utilizes Apache Iceberg for table format, enabling ACID transactions and schema evolution.
- **Scalable Transformations**: dbt + DuckDB for high-performance transformations directly on S3 data.
- **Federated Query Engine**: Trino for distributed SQL queries across different catalogs.
- **Interactive BI**: Apache Superset for dashboarding and data exploration.
- **Orchestration**: Apache Airflow managing the daily E2E pipeline.
- **Developer Friendly**: Managed with `uv` for blazing-fast environment setup and `Makefile` for one-click operations.

---

## 🛠️ Tech Stack & Architecture

<div align="center">
  <img src="images/architecture.png" alt="Data Lakehouse Architecture" width="800">
</div>

| Layer | Component | Technology | Description |
| :--- | :--- | :---: | :--- |
| **Ingestion** | Crawler | 🐍 Python | Scrapes Tiki API, sanitizes data, and uploads to MinIO as `Parquet`. |
| **Storage** | Object Store | 🪣 MinIO | S3-compatible storage for Raw (Bronze) and Iceberg (Silver/Gold) layers. |
| **Metadata** | Metastore | 🐘 Postgres | Stores Iceberg metadata and Trino catalog info. |
| **Compute** | SQL Engine | ⚡ Trino | Distributed engine for querying Iceberg tables via SQL. |
| **Transform** | Data Modeling | 🔨 dbt + DuckDB | Transforms raw JSON/Parquet into structured analytics models. |
| **Orchestration** | Scheduler | 🌬️ Airflow | Orchestrates the full Crawl -> Transform -> Analytics flow. |
| **Visualization** | BI Tool | 📊 Superset | Connected to Trino for building interactive dashboards. |

---

## 📂 Project Structure

```text
tiki-lakehouse/
├── .github/workflows/       # CI/CD (Formatting & dbt linting)
├── airflow_home/            # Airflow configurations and local DB
├── crawler/                 # Python ingestion scripts
│   ├── tests/               # Pytest scripts for crawler
│   └── fetch_tiki.py        # Main extraction script
├── dags/                    # Airflow DAG definitions
│   └── tiki_lakehouse_dag.py # Daily pipeline DAG
├── dbt_tiki/                # dbt project for transformations
│   ├── models/              # Staging & Marts models
│   ├── dbt_project.yml      
│   └── profiles.yml         # DuckDB S3 configuration
├── trino/                   # Trino configuration (Catalogs, Node, etc.)
│   └── etc/catalog/         # Iceberg & Hive catalog properties
├── Makefile                 # Shortcut commands for orchestration
├── docker-compose.yml       # Infrastructure (MinIO, Trino, Postgres, Superset)
├── run_project.sh           # One-click initialization script
└── pyproject.toml           # Python dependencies (uv managed)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- [uv](https://github.com/astral-sh/uv) (Blazing fast Python package manager)

### 2. Quick Launch (Automated)
The easiest way to start is using the provided bash script which handles environment setup, infrastructure, and the first data run:
```bash
chmod +x run_project.sh
./run_project.sh
```

### 3. Manual Step-by-Step Setup
If you prefer to run things manually:

**Step A: Prepare Environment**
```bash
cp .env.example .env  # Edit with your credentials
make setup            # Install dependencies via uv
```

**Step B: Spin up Infrastructure**
```bash
make up               # Start Docker containers (MinIO, Trino, etc.)
```

**Step C: Execute Pipeline**
```bash
make crawl            # Fetch data from Tiki to MinIO
make dbt-run          # Transform data to Iceberg tables
```

---

## 🔗 Monitoring & Access

| Service | URL | Credentials (Default) |
| :--- | :--- | :--- |
| **MinIO Console** | `http://localhost:9001` | `admin` / `minio_password` |
| **Trino UI** | `http://localhost:8080` | `admin` |
| **Apache Superset** | `http://localhost:8088` | `admin` / `admin` |
| **Airflow Webserver**| `http://localhost:8081` | (Standalone mode, check terminal) |

---

## 📊 Data Pipeline Flow

1.  **Bronze Layer (Raw)**: `crawler/fetch_tiki.py` fetches data from Tiki's listing API. It handles nested structures by stringifying complex objects and saves them as **Parquet** files in the `raw-data` bucket in MinIO.
2.  **Silver Layer (Staging)**: dbt staging models (`stg_tiki_books.sql`) read raw Parquet files, cast types, and flatten nested JSON strings using DuckDB's JSON extensions.
3.  **Gold Layer (Marts)**: Final fact tables (`fct_tiki_books.sql`) are materialized as **Apache Iceberg** tables in MinIO. These are optimized for high-performance querying.
4.  **Analytics**: Trino queries the Gold layer, and Superset visualizes it. A separate `analytics_plot.py` script can also be used to generate static charts.

---

## 🌬️ Airflow Orchestration

To run the automated daily pipeline:
```bash
make airflow-start
```
The DAG `tiki_lakehouse_daily_pipeline` will appear in the UI, managing the sequence:
`Crawl` ➔ `dbt Transformation` ➔ `Generate Analytics`

---

## 🛠️ Makefile Reference

| Command | Description |
| :--- | :--- |
| `make setup` | Create venv and install all dependencies |
| `make up` | Start all Docker services (detached) |
| `make down` | Stop and remove Docker services |
| `make crawl` | Run the Tiki product crawler |
| `make dbt-run` | Run dbt transformations (Staging & Marts) |
| `make lint` | Run Black, Flake8, and SQLFluff linters |
| `make test` | Run crawler unit tests |
| `make airflow-start` | Start Airflow standalone server |

---

## 🖼️ Screenshots Gallery

### 1. Ingestion & Storage
<p align="center">
  <img src="images/01-tiki-listings.png" width="45%" alt="Tiki Listings">
  <img src="images/04-s3-storage.png" width="45%" alt="MinIO S3 Storage">
</p>

### 2. Infrastructure & Analytics
<p align="center">
  <img src="images/02-run-project.png" width="45%" alt="Run Project">
  <img src="images/top_10_books.png" width="45%" alt="Analytics Plot">
</p>

### 3. Superset Dashboards
<img src="images/05.04-superset-demo-dashboard.png" width="100%" alt="Superset Dashboard">

---

_Author: @tunguyenn99 - Built with ❤️ for the Data Community_
