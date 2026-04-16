# Tiki Lakehouse Project

This project simulates a Modern Data Stack locally using Open Source tools, designed as a comprehensive data engineering and analytics setup.

## Architecture

1. **Ingestion**: Python crawls Tiki API, saves files as Parquet to `raw-data` bucket.
2. **Storage**: **MinIO** stores data files (simulated S3).
3. **Metastore**: **PostgreSQL** serves as a JDBC metastore mapping tables and schemas.
4. **Transform**: **dbt** with `dbt-duckdb` adapter reads raw data from `raw-data` bucket, applies transformations, and creates external tables mapped back to `lakehouse` bucket.
5. **Query Engine**: **Trino** queries the unified data over Iceberg/Parquet mapping.
6. **BI Tool**: **Apache Superset** connects to Trino for blazing fast dashboards.

## Quick Start

### 1. Launch Infrastructure
```bash
cd tiki-lakehouse
docker compose up -d
```
Check connections:
- MinIO: `http://localhost:9001` (admin/minio_password)
- Trino UI: `http://localhost:8080` (use any username like `admin`)
- Superset: `http://localhost:8088` (admin/admin_password)

### 2. Crawl Data
```bash
cd crawler
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python fetch_tiki.py
```
Check MinIO to see the raw parquet file uploaded to `raw-data/tiki_products/`.

### 3. Transform (dbt)
```bash
cd dbt_tiki
# Install the dbt-duckdb physical connector
pip install dbt-duckdb
dbt run
```
