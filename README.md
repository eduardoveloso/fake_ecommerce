
# Fake E-commerce Data Pipeline

Este projeto simula um fluxo de dados completo para um e-commerce, incluindo geração, ingestão, transformação e armazenamento de dados de pedidos. A estrutura foi projetada para ser simples e utiliza ferramentas de ETL e orquestração para automatizar o processo.

## Visão Geral do Projeto

O propósito deste projeto é criar um pipeline de dados simulado para um e-commerce, permitindo explorar o processo de ingestão, transformação e carregamento de dados (ETL) de pedidos de maneira automatizada e escalável. Utilizando o Airflow para orquestração, o pipeline gera dados sintéticos de pedidos, armazena-os em um bucket S3, transforma os dados e, em seguida, os carrega em um banco de dados PostgreSQL.

### Fluxo de Dados

1. **Geração de Dados**: Um script gera dados fake de pedidos em formato JSON para simular pedidos de e-commerce.
2. **Armazenamento em S3**: Os dados gerados são armazenados em um bucket S3 para persistência e futura transformação.
3. **Transformação de Dados**: Usando scripts de ETL, os dados no S3 são transformados e preparados para análise.
4. **Armazenamento em PostgreSQL**: Após a transformação, os dados são carregados em um banco de dados PostgreSQL.
5. **Orquestração com Airflow**: O Apache Airflow gerencia e orquestra cada etapa do pipeline, garantindo a execução e a coordenação dos processos.

![Arquitetura](https://lh7-rt.googleusercontent.com/docsz/AD_4nXc9-p4_nETi7LC5ITX2lhugWPpAWorGEHkLCEvTPgloFmnXTaE73pKEk9B5sxA49f9JpvyRgcKsuALVQ_KAnh130bFoaezxkIQ6bWXUSuJQbA7Xs9CiTmZ6pARkZRTwpuL2mZAoIh0ViTsqm6Z4IKE7sUQP?key=RymDh7qbhCFSE8YzTt8rCw)

## Estrutura de Diretórios

- `dags/`: Contém os arquivos de DAG do Airflow para orquestração do pipeline, incluindo scripts de ETL e ingestão.
- `data/`: Contém o arquivo JSON simulado com dados de pedidos (`orders_data_1727041454-2.json`).
- `jobs/`: Diretório reservado para futuros trabalhos e processos de dados.
  - `utils/`: Scripts utilitários que incluem:
    - `fake_generator.py`: Gera dados sintéticos de pedidos.
    - `upload_s3.py`: Script para fazer upload dos dados no S3.
    - `ingestion_process.py`: Processa a ingestão de dados.
- `test/`: Scripts de teste para validação do pipeline, incluindo um exemplo de ETL (`etl_example.py`)
- `docker-compose.yaml`: Configuração do Docker para inicializar todos os serviços.
- `requirements.txt`: Dependências do Python necessárias para rodar o projeto.

## Requisitos

- **Docker** e **Docker Compose** para facilitar o setup do ambiente.
- Uma conta e credenciais da AWS configuradas para o acesso ao S3.

## Como Executar o Projeto

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/eduardoveloso/fake_ecommerce.git
   cd fake_ecommerce
   ```

2. **Configurar as variáveis de ambiente**:
   - Edite o arquivo `.env` com as credenciais da AWS e configurações do PostgreSQL.

3. **Iniciar o ambiente com Docker Compose**:

   ```bash
   docker-compose up -d
   ```

4. **Acessar o Airflow**:
   - O Airflow estará disponível em `http://localhost:8080` (consulte o docker-compose.yaml para confirmar a porta).
   - Use a interface do Airflow para monitorar e gerenciar o pipeline.

## Principais Dependências

- **Python**: Linguagem principal para scripts e processamento de dados.
- **Apache Airflow**: Orquestração do pipeline ETL.
- **AWS S3**: Armazenamento temporário dos dados simulados.
- **PostgreSQL**: Banco de dados para armazenamento final dos dados transformados.

## Notas

- Certifique-se de que o Docker e Docker Compose estão instalados e funcionando corretamente.
- As DAGs do Airflow são configuradas para execução automática, mas podem ser executadas manualmente pela interface do Airflow para testes e validação.
