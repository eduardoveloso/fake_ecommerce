import os
import sys

project_path = os.path.dirname(__file__).split("/fake_ecommerce/")[0] + "/fake_ecommerce/"
sys.path.append(project_path)

from utils.fake_generator import generate_orders
from utils.upload_s3 import upload_to_s3
from dotenv import load_dotenv, find_dotenv
from random import randint
import time

def generate_filename(base_name: str, extension: str):
    timestamp = int(time.time())
    full_name = f"{base_name}_{timestamp}.{extension}"
    return full_name


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

total_orders = randint(1,20)
looping_file_generator = randint(1,5)

count = 1
while count <= looping_file_generator:
    json_data = generate_orders(total_orders)
    upload_to_s3(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_region_name=AWS_REGION,
        bucket_name=AWS_BUCKET_NAME,
        file_name=generate_filename(base_name="orders_data", extension="json"),
        data=json_data,
    )
    time.sleep(10)
    count+=1