from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 0,
}

def print_hello():
    print("Hello from Airflow!")
    return "Task completed"

with DAG(
    dag_id='hello_test',
    default_args=default_args,
    description='Simple test DAG to write hello in logs',
    schedule=None,
    catchup=False,
) as dag:
    
    hello_task = PythonOperator(
        task_id='hello_task',
        python_callable=print_hello,
    )

    hello_task
