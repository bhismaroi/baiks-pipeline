from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.decorators import task_group
from airflow.models import Variable
from utils.extract import extract_table, extract_api
from utils.load import load_table, load_api
from utils.slack_alert import slack_alert
from airflow.datasets import Dataset

@task_group(group_id='extract')
def extract_group():
    @task_group(group_id='db')
    def db_extract_group():
        default_tables = {
            'person': ['person', 'businessentityid'],
            'employee': ['humanresources', 'businessentityid'],
            'product': ['production', 'productid'],
            'shipmethod': ['purchasing', 'shipmethodid'],
            'currencyrate': ['sales', 'currencyrateid']
        }
        tables = Variable.get("BIKES_STORE_STAGING__table_to_extract_and_load", default_var=default_tables, deserialize_json=True)
        
        tasks = []
        for table, details in tables.items():
            schema, key = details
            tasks.append(PythonOperator(
                task_id=f'extract_{table}',
                python_callable=extract_table,
                op_kwargs={'table': table, 'schema': schema, 'key': key, 'execution_date': '{{ ds }}'},
                outlets=[Dataset(f"s3://bikes-store/{table}_{{{{ ds }}}}.csv")]
            ))
        return tasks

    @task_group(group_id='api')
    def api_extract_group():
        return PythonOperator(
            task_id='extract_api',
            python_callable=extract_api,
            op_kwargs={'execution_date': '{{ ds }}'},
            outlets=[Dataset(f"s3://bikes-store/currency_data_{{{{ ds }}}}.csv")]
        )

    return db_extract_group() + [api_extract_group()]

@task_group(group_id='load')
def load_group():
    @task_group(group_id='db')
    def db_load_group():
        default_tables = {
            'person': ['person', 'businessentityid'],
            'employee': ['humanresources', 'businessentityid'],
            'product': ['production', 'productid'],
            'shipmethod': ['purchasing', 'shipmethodid'],
            'currencyrate': ['sales', 'currencyrateid']
        }
        tables = Variable.get("BIKES_STORE_STAGING__table_to_extract_and_load", default_var=default_tables, deserialize_json=True)
        
        ordered_tables = [
            'person', 'employee', 'product', 'shipmethod', 'currencyrate',
            'salesreason', 'salesterritory', 'specialoffer', 'salesperson',
            'store', 'customer', 'specialofferproduct', 'salespersonquotahistory',
            'salesterritoryhistory', 'shoppingcartitem', 'salesorderheader',
            'salesorderdetail', 'salesorderheadersalesreason'
        ]
        tasks = []
        for table in ordered_tables:
            tasks.append(PythonOperator(
                task_id=f'load_{table}',
                python_callable=load_table,
                op_kwargs={'table': table, 'execution_date': '{{ ds }}'},
                outlets=[Dataset(f"postgresql://warehouse/staging/{table}")],
                trigger_rule='all_done'
            ))
        return tasks

    @task_group(group_id='api')
    def api_load_group():
        return PythonOperator(
            task_id='load_api',
            python_callable=load_api,
            op_kwargs={'execution_date': '{{ ds }}'},
            outlets=[Dataset("postgresql://warehouse/staging/currency_data")]
        )

    return db_load_group() + [api_load_group()]

with DAG(
    dag_id='bikes_store_staging',
    description='Extract data and load into staging area',
    start_date=datetime(2024, 9, 1),
    schedule_interval='@daily',
    on_failure_callback=slack_alert,
    catchup=False
) as dag:
    extract_tasks = extract_group()
    load_tasks = load_group()
    trigger = TriggerDagRunOperator(
        task_id='trigger_bikes_store_warehouse',
        trigger_dag_id='bikes_store_warehouse',
        wait_for_completion=False
    )
    
    # Chain the task groups
    for task in extract_tasks:
        task >> load_tasks
    load_tasks[-1] >> trigger