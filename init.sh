#!/bin/bash
set -e

# Migrar o banco de dados do Airflow
airflow db migrate

# Instalar as dependências
pip install -r /fake_ecommerce_app/requirements.txt

# Verificar qual serviço está sendo iniciado
if [ "$SERVICE" = "webserver" ]; then
    # Criar usuário administrador se estiver iniciando o webserver
    airflow users create \
        -u admin \
        -f eduardo \
        -l veloso \
        -r Admin \
        -e "$AIRFLOW_WWW_USER_EMAIL" \
        --password "$AIRFLOW_WWW_USER_PASSWORD"
    # Iniciar o webserver do Airflow
    exec airflow webserver
elif [ "$SERVICE" = "scheduler" ]; then
    # Iniciar o scheduler do Airflow
    exec airflow scheduler
else
    echo "Serviço desconhecido: $SERVICE"
    exit 1
fi
