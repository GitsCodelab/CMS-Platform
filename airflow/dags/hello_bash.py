from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries':  0,
}

with DAG(
    dag_id='hello_bash',
    default_args=default_args,
    description='Simple bash test DAG',
    schedule=None,
    catchup=False,
) as dag:
    
    hello_task = BashOperator(
        task_id='hello_bash_task',
        bash_command='echo "Hello from Bash! Airflow is working!"',
    )

    hello_task
