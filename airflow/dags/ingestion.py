from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys
import os

project_path = (
    os.path.dirname(__file__).split("/fake_ecommerce/")[0] + "/fake_ecommerce/"
)
sys.path.append(project_path)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

def ingestion_process():
    import src.ingestion_process


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
    "ingestion_process",
    default_args=default_args,
    description="A simple DAG to run ingestion_process.py",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 9, 22),
    catchup=False,
)

run_this = PythonOperator(
    task_id="run_ingestion_process",
    python_callable=ingestion_process,
    dag=dag,
)

run_this
