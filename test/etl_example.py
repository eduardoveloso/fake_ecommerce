import pandas as pd
import json

file_path = "/Users/eduardoveloso/Documents/projects/fake_ecommerce/data/orders_data_1727041454-2.json"
with open(file_path) as json_file:
    json_list = json.load(json_file)

df = pd.DataFrame(json_list["orders"])

df_orders = (
    df[["order_date", "order_id", "user_id", "qty", "unit_price"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
print(df_orders)
