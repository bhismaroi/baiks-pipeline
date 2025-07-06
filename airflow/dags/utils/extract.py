import pandas as pd
from sqlalchemy import create_engine
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import requests
from airflow.models import Variable
from airflow.datasets import Dataset

def get_db_connection():
    """Create a SQLAlchemy engine for the transaction database."""
    return create_engine('postgresql+psycopg2://postgres:postgres@sources-postgres:5432/postgres')

def get_s3_hook():
    """Create an S3Hook for MinIO interactions."""
    return S3Hook(aws_conn_id='s3-conn')

def extract_table(table, schema, key, execution_date):
    """
    Extract data from a PostgreSQL table and save as CSV in MinIO.
    
    Args:
        table (str): Name of the table to extract.
        schema (str): Schema of the table.
        key (str or list): Primary key(s) for incremental extraction.
        execution_date (str): Airflow execution date for incremental filtering.
    
    Returns:
        Dataset: Dataset URI for the saved CSV.
    """
    engine = get_db_connection()
    s3_hook = get_s3_hook()
    incremental = Variable.get("BIKES_STORE_STAGING_INCREMENTAL_MODE") == "True"
    
    query = f"SELECT * FROM {schema}.{table}"
    if incremental and isinstance(key, str):
        query += f" WHERE {key} >= '{execution_date}'"
    elif incremental and isinstance(key, list):
        query += f" WHERE {key[0]} >= '{execution_date}'"
    
    df = pd.read_sql(query, engine)
    csv_buffer = df.to_csv(index=False)
    s3_key = f"bikes-store/{table}_{execution_date}.csv"
    s3_hook.load_string(csv_buffer, s3_key, bucket_name='bikes-store', replace=True)
    
    return Dataset(f"s3://bikes-store/{table}_{execution_date}.csv")

def extract_api(execution_date):
    """
    Extract data from the currency API and save as CSV in MinIO.
    
    Args:
        execution_date (str): Airflow execution date for file naming.
    
    Returns:
        Dataset: Dataset URI for the saved CSV.
    """
    url = Variable.get("BIKES_STORE_API_URL")
    response = requests.get(url)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    s3_hook = get_s3_hook()
    
    csv_buffer = df.to_csv(index=False)
    s3_key = f"bikes-store/currency_data_{execution_date}.csv"
    s3_hook.load_string(csv_buffer, s3_key, bucket_name='bikes-store', replace=True)
    
    return Dataset(f"s3://bikes-store/currency_data_{execution_date}.csv")