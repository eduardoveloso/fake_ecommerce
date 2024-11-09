from airflow import DAG
from airflow.decorators import task, dag
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import pandas as pd
import os
import logging
import json

# Configuração para AWS e boto3 session
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_PREFIX_ORIGIN = "landing_zone/fakecommerce/"
AWS_PREFIX_DESTINATION = "processed_zone/fakecommerce/"

# Configura o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Argumentos padrão para DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["eveloso92@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    dag_id="etl_process",
    schedule_interval=None,
    start_date=datetime(2023, 10, 13),
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    concurrency=5,
    tags=["fake_ecommerce", "etl", "S3"],
)
def s3_etl_pipeline():
    # -- Task 0: Iniciar DAG --
    @task
    def start():
        EmptyOperator(task_id="start")

    # --- Task 1: Validar e criar tabelas no Postgres, se necessário ---
    @task
    def validate_and_create_tables(task_id="create_postgres_tables"):
        logging.info("Validando se as tabelas existem no Postgre RDS...")

        pg_hook = PostgresHook(postgress_connection_id="postgres_default")
        connection = pg_hook.get_conn()
        cursor = connection.cursor()

        table_creation_queries = [
            """
            CREATE TABLE IF NOT EXISTS dim_produto (
                product_id INT PRIMARY KEY,
                product_name VARCHAR(255),
                category VARCHAR(50)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS dim_cliente (
                user_id VARCHAR(50) PRIMARY KEY
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS dim_data (
                order_date_id INT PRIMARY KEY,
                order_date DATE,
                year INT,
                month INT,
                day INT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS dim_pagamento (
                payment_type_id INT PRIMARY KEY,
                payment_type VARCHAR(50)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS dim_cupom (
                coupon_id INT PRIMARY KEY,
                coupon VARCHAR(50)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS fato_pedidos (
                order_id VARCHAR(50) PRIMARY KEY,
                user_id VARCHAR(50),
                product_name VARCHAR(255),
                order_date DATE,
                qty INT,
                unit_price DECIMAL,
                total_value DECIMAL,
                payment_type VARCHAR(50),
                coupon VARCHAR(50)
            );
            """,
        ]

        for query in table_creation_queries:
            cursor.execute(query)
            logging.info(
                f"Tabela {query.split('CREATE TABLE IF NOT EXISTS ')[1].split(' (')[0]} criada ou já existente."
            )

        connection.commit()
        cursor.close()
        connection.close()
        logging.info("Validação e criação das tabelas concluída.")

    # --- Task 2: Listar arquivos JSON no S3 ---
    @task
    def list_files_in_s3():
        logging.info(
            f"Listando arquivos no bucket {AWS_BUCKET_NAME} com o prefixo {AWS_PREFIX_ORIGIN}..."
        )
        s3_hook = S3Hook(aws_conn_id="aws_conn")
        s3_keys = s3_hook.list_keys(
            bucket_name=AWS_BUCKET_NAME, prefix=AWS_PREFIX_ORIGIN
        )
        json_files = [key for key in s3_keys if key.endswith(".json")]
        logging.info(f"Arquivos encontrados: {json_files}")
        return json_files

    # --- Task 3: Extrair arquivos JSON do S3 ---
    @task
    def extract_from_s3(json_files):
        logging.info(f"Extraindo arquivo {json_files} do bucket {AWS_BUCKET_NAME}...")

        s3_hook = S3Hook(aws_conn_id="aws_conn")
        s3_object = s3_hook.get_key(key=json_files, bucket_name=AWS_BUCKET_NAME)
        json_content = s3_object.get()["Body"].read().decode("utf-8")

        order = json.loads(json_content)
        logging.info(f"Dados extraídos com sucesso: {order}")

        return order

    # --- Task 4: Transformar os dados para o formato Star Schema ---
    @task
    def transform_and_load(orders):
        logging.info("Transformando os dados...")

        all_orders = []
        for json_file in orders:  # Itera diretamente sobre os JSONs
            all_orders.extend(json_file["orders"])
        df_order = pd.DataFrame(all_orders)

        # Dimensão Produto
        dim_produto = df_order[["product_name", "category"]].drop_duplicates().reset_index(drop=True)
        dim_produto["product_id"] = dim_produto.index + 1  # Criando IDs para produtos

        # Dimensão Cliente
        dim_cliente = df_order[["user_id"]].drop_duplicates().reset_index(drop=True)

        # Dimensão Data
        df_order["order_date"] = pd.to_datetime(df_order["order_date"])
        dim_data = df_order[["order_date"]].drop_duplicates().reset_index(drop=True)
        dim_data["order_date_id"] = dim_data.index + 1
        dim_data["year"] = dim_data["order_date"].dt.year
        dim_data["month"] = dim_data["order_date"].dt.month
        dim_data["day"] = dim_data["order_date"].dt.day

        # Dimensão Tipo de Pagamento
        dim_pagamento = df_order[["payment_type"]].drop_duplicates().reset_index(drop=True)
        dim_pagamento["payment_type_id"] = dim_pagamento.index + 1

        # Dimensão Cupom
        dim_cupom = df_order[["coupon"]].drop_duplicates().reset_index(drop=True)
        dim_cupom["coupon_id"] = dim_cupom.index + 1

        # Tabela Fato (Fato Pedidos)
        df_order["qty"] = df_order["qty"].astype(int)
        df_order["unit_price"] = df_order["unit_price"].astype(float)
        df_order["total_value"] = df_order["qty"] * df_order["unit_price"]
        fato_pedidos = df_order[
            [
                "order_id",
                "user_id",
                "product_name",
                "order_date",
                "qty",
                "unit_price",
                "total_value",
                "payment_type",
                "coupon",
            ]
        ]

        logging.info("Transformação concluída.")

        # -----Load into database

        pg_hook = PostgresHook(postgres_conn_id="postgres_app")
        connection = pg_hook.get_conn()
        cursor = connection.cursor()

        def load_dimension_with_deduplication(df, table_name, columns):
            for row in df.itertuples(index=False, name=None):
                placeholders = ", ".join(["%s"] * len(row))
                columns_str = ", ".join(columns)
                query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;"
                cursor.execute(query, row)

        print("Salvando dados dim_produto")
        load_dimension_with_deduplication(dim_produto, "dim_produto", ["product_name", "category", "product_id"])

        print("Salvando dados dim_cliente")
        load_dimension_with_deduplication(dim_cliente, "dim_cliente", ["user_id"])

        print("Salvando dados dim_pagamento")
        load_dimension_with_deduplication(dim_pagamento, "dim_pagamento", ["payment_type", "payment_type_id"])

        print("Salvando dados dim_cupom")
        load_dimension_with_deduplication(dim_cupom, "dim_cupom", ["coupon", "coupon_id"])

        print("Salvando dados fato_pedidos")
        load_dimension_with_deduplication(
            fato_pedidos,
            "fato_pedidos",
            [
                "order_id",
                "user_id",
                "product_name",
                "order_date",
                "qty",
                "unit_price",
                "total_value",
                "payment_type",
                "coupon",
            ]
        )

    # -- Task 5: Finalizar DAG --

    @task
    def end():
        EmptyOperator(task_id="end")

    start_task = start()
    validate_task = validate_and_create_tables()
    list_files_task = list_files_in_s3()
    extract_from_s3_task = extract_from_s3.expand(json_files=list_files_task)
    transformed_data = transform_and_load(extract_from_s3_task)
    end_task = end()

    start_task >> validate_task >> list_files_task >> extract_from_s3_task >> transformed_data >> end_task

dag = s3_etl_pipeline()
