# Bikes Store Pipeline

## Project Overview
This project implements a data pipeline for Bikes Store, extracting data from a PostgreSQL transaction database and an external API, storing it in a MinIO data lake, loading it into a staging schema, and transforming it into a data warehouse using DBT. The pipeline is orchestrated using Apache Airflow with monitoring via StatsD, Prometheus, and Grafana.

## Architecture
- **Airflow**: Orchestrates the ETL pipeline (version 2.10.2, CeleryExecutor).
- **PostgreSQL**: Transaction database (`sources-postgres`) and data warehouse (`warehouse-postgres`).
- **MinIO**: Data lake with buckets `airflow-logs` and `bikes-store`.
- **Monitoring**: StatsD, Prometheus, Grafana for Airflow metrics.
- **DBT**: Transforms data from staging to warehouse schema.
- **Slack**: Alerts for DAG failures.

## How to Run
1. Install Docker and Docker Compose on WSL Ubuntu.
2. Clone the repository: `git clone <repo-url>`.
3. Navigate to `bikes-store-pipeline/`.
4. Run `chmod +x scripts/*.sh` to make scripts executable.
5. Execute `./scripts/setup.sh` to install dependencies, create MinIO buckets, and import Airflow variables & connections (make sure `data/airflow_connections_init.yaml` already contains your Slack **Bot** token).
6. Start Airflow and data services: `docker-compose -f airflow/docker-compose.yml up -d`.
7. Start monitoring services: `docker-compose -f docker-compose-monitoring.yml up -d`.
8. Access Airflow UI at `http://localhost:8080` (login: **airflow/airflow**).
9. Access Grafana at `http://localhost:3000` (default login: admin/admin).
10. Trigger `bikes_store_staging` DAG in Airflow UI to start the pipeline.

## Screenshots
- Airflow DAG View: [Insert screenshot]
- Grafana Dashboard: [Insert screenshot]
- MinIO Buckets: [Insert screenshot]

## Validation
- All services (Airflow, PostgreSQL, MinIO, monitoring) run smoothly.
- DAGs are visible and executable in Airflow UI.
- Data is extracted to MinIO, loaded to staging, and transformed to warehouse.
- GitHub repository contains all files and documentation.