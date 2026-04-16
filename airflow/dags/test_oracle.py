from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.oracle.hooks.oracle import OracleHook

def test_oracle_conn():
    hook = OracleHook(oracle_conn_id='oracle_main')
    conn = hook.get_conn()
    cur = conn.cursor()
    cur.execute('select name from v$database')
    result = cur.fetchone()
    print('oracle test result:', result)
    cur.close()
    try:
        conn.close()
    except Exception:
        pass

def test_postgres_conn():
    hook = PostgresHook(postgres_conn_id='postgres_main')
    with hook.get_conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT NOW()')
        result = cur.fetchone()
        print('postgres test result:', result)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG('test_connections', default_args=default_args, schedule=None, catchup=False) as dag:
    t_oracle = PythonOperator(task_id='test_oracle', python_callable=test_oracle_conn)
    t_postgres = PythonOperator(task_id='test_postgres', python_callable=test_postgres_conn)
