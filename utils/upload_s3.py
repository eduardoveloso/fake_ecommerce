import boto3
from botocore.exceptions import ClientError
import json




def upload_to_s3(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_region_name: str,
    bucket_name: str,
    file_name: str,
    data: dict,
):
    client = boto3.client(
        "s3",
        aws_region_name=aws_region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    try:
        json_data = json.dumps(data)
    except (TypeError, ValueError) as e:
        print(f"Erro ao serializar os dados: {e}")

    try:
        object_key = f"ecommerce_files/raw/new_file/{file_name}"
        client.put_object(Bucket=bucket_name, Key=object_key, Body=json_data, ContentType="application/json")
        print(f"Dados enviados com sucesso para s3://{bucket_name}/{object_key}")
    except ClientError as e:
        print(f"Erro ao fazer upload para o S3: {e}")

    return None
