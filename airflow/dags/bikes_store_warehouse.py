from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig
from airflow.models import Variable
from utils.slack_alert import slack_alert
import os

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_warehouse_init():
    """Check if warehouse initialization is required."""
    init = Variable.get("BIKES_STORE_WAREHOUSE_INIT", default_var="False") == "True"
    return 'warehouse_init' if init else 'warehouse'

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='bikes_store_warehouse',
    description='Transform data into warehouse models',
    start_date=datetime(2024, 7, 1),
    schedule_interval=None,
    on_failure_callback=slack_alert,
    catchup=False,
    default_args=default_args,
    tags=['dbt', 'warehouse']
) as dag:
    # Branch to determine if we need to initialize the warehouse
    check_init = BranchPythonOperator(
        task_id='check_is_warehouse_init',
        python_callable=check_warehouse_init
    )

    # Configure dbt project
    dbt_project_path = os.getenv('DBT_PROJECT_DIR', '/opt/airflow/dbt/bikes_store_dbt')
    
    project_config = ProjectConfig(
        dbt_project_path=dbt_project_path,
    )
    
    profile_config = ProfileConfig(
        profile_name='bikes_store',
        target_name='dev',
        profiles_yml_filepath=Path(dbt_project_path) / 'profiles.yml'
    )

    # Warehouse initialization task group (runs full refresh)
    warehouse_init = DbtTaskGroup(
        group_id='warehouse_init',
        dbt_project_path=dbt_project_path,
        profile_config=profile_config,
        operator_args={
            'install_deps': True,
            'full_refresh': True
        },
        test_behavior='after_all',
        dbt_args={
            'dbt_executable_path': 'dbt',
            'vars': '{}'
        }
    )

    # Regular warehouse update task group (incremental)
    warehouse = DbtTaskGroup(
        group_id='warehouse',
        dbt_project_path=dbt_project_path,
        profile_config=profile_config,
        operator_args={
            'install_deps': False,
            'full_refresh': False
        },
        test_behavior='after_all',
        dbt_args={
            'dbt_executable_path': 'dbt',
            'exclude': 'dim_date',
            'vars': '{}'
        }
    )

    # Set up task dependencies
    check_init >> [warehouse_init, warehouse]