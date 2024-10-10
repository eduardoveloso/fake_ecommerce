from faker import Faker
import faker_commerce
from random import randint
from datetime import datetime
from zoneinfo import ZoneInfo

def generate_orders(qty: int) -> dict:
    fake = Faker("en_US")
    fake.add_provider(faker_commerce.Provider)
    payment_type = ["credit","debit","money"]
    coupon = ["not applied", "cp5","cp10"]
    time_zone_br = ZoneInfo("America/Sao_Paulo")

    final_dict = {"orders": []}
    for _ in range(qty):
        init_dict = {
            "order_id": fake.lexify(text="?????", letters="0123456789"),
            "order_date": fake.date_between_dates(date_start=datetime(2024,1,1), date_end=datetime(2024,9,22)).isoformat(),
            "user_id": fake.lexify(text="usr-????", letters="0123456789"),
            "product_name": fake.ecommerce_name(),
            "category": fake.ecommerce_category(),
            "qty": f"{randint(1, 3)}",
            "unit_price": f"{fake.pyfloat(right_digits=2, min_value=5, max_value=110)}",
            "payment_type": payment_type[randint(0, 2)],
            "coupon": f"{coupon[randint(0, 2)]}",
            "date_ingestion": datetime.now(time_zone_br).isoformat(),
        }
        final_dict["orders"].append(init_dict)

    return final_dict