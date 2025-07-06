#!/bin/bash
# Install dependencies
pip install -r requirements.txt
set -a
source .env
set +a

# Initialize MinIO buckets
docker-compose -f airflow/docker-compose.yml up -d minio
sleep 10
docker run --network=host minio/mc mb minio/airflow-logs
docker run --network=host minio/mc mb minio/bikes-store
echo "Using MINIO_ACCESS_KEY: $MINIO_ACCESS_KEY"

# Initialize Airflow variables and connections
docker-compose -f airflow/docker-compose.yml up -d airflow-webserver
sleep 10
docker exec $(docker ps -q -f name=airflow-webserver) airflow variables import /opt/airflow/variables.json
docker exec $(docker ps -q -f name=airflow-webserver) airflow connections import /opt/airflow/connections.yaml