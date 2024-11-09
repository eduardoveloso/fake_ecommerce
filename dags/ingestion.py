import sys
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

sys.path.append("/fake_ecommerce_app/airflow/")

def ingestion_process():
    import jobs.ingestion_process


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["eveloso92@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    dag_id="ingestion_process",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval=None,
    start_date=datetime(2024, 9, 22),
    catchup=False,
    tags=["fake_ecommerce", "ingestion", "S3"]
)

start_task = EmptyOperator(task_id="start", dag=dag)
end_task = EmptyOperator(task_id="end", dag=dag)

ingestion = PythonOperator(
    task_id="run_ingestion_process",
    python_callable=ingestion_process,
    dag=dag,
)

start_task >> ingestion >> end_task
