import pandas as pd
from sqlalchemy import create_engine
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
from airflow.datasets import Dataset

def get_warehouse_connection():
    """Create a SQLAlchemy engine for the data warehouse."""
    return create_engine('postgresql+psycopg2://postgres:postgres@warehouse-postgres:5432/postgres')

def get_s3_hook():
    """Create an S3Hook for MinIO interactions."""
    return S3Hook(aws_conn_id='s3-conn')

def load_table(table, execution_date):
    """
    Load data from MinIO CSV to the staging schema in PostgreSQL.
    
    Args:
        table (str): Name of the table to load.
        execution_date (str): Airflow execution date for file naming.
    
    Returns:
        Dataset: Dataset URI for the loaded table.
    """
    engine = get_warehouse_connection()
    s3_hook = get_s3_hook()
    incremental = Variable.get("BIKES_STORE_STAGING_INCREMENTAL_MODE") == "True"
    
    s3_key = f"bikes-store/{table}_{execution_date}.csv"
    csv_obj = s3_hook.get_key(s3_key, bucket_name='bikes-store')
    df = pd.read_csv(csv_obj)
    
    if incremental:
        df.to_sql(table, engine, schema='staging', if_exists='append', index=False)
    else:
        df.to_sql(table, engine, schema='staging', if_exists='replace', index=False)
    
    return Dataset(f"postgresql://warehouse/staging/{table}")

def load_api(execution_date):
    """
    Load API data from MinIO CSV to the staging schema in PostgreSQL.
    
    Args:
        execution_date (str): Airflow execution date for file naming.
    
    Returns:
        Dataset: Dataset URI for the loaded table.
    """
    engine = get_warehouse_connection()
    s3_hook = get_s3_hook()
    
    s3_key = f"bikes-store/currency_data_{execution_date}.csv"
    csv_obj = s3_hook.get_key(s3_key, bucket_name='bikes-store')
    df = pd.read_csv(csv_obj)
    
    df.to_sql('currency_data', engine, schema='staging', if_exists='replace', index=False)
    
    return Dataset(f"postgresql://warehouse/staging/currency_data")