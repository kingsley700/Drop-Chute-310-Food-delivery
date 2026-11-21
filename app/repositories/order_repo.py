import json

from app.schemas.order import Order

filep = "data/orders.json"



def _read_data():
    with open(filep, "r", encoding="utf-8") as file:
        text = file.read().strip()
    return json.loads(text) if text else []


def _write_data(orders):
    with open(filep, "w", encoding="utf-8") as file:
        json.dump(orders, file, indent=2)


# Get orders
def get_orders():
    return [Order(**record) for record in _read_data()]


def get_order_by_id(order_id: int):
    for order in get_orders():
        if order.id == order_id:
            return order
    return None



def get_orders_by_customer(customer_id: int):
    orders = [order for order in get_orders() if order.customer_id == customer_id]
    return sorted(orders, key=lambda order: order.created_at, reverse=True)


def create_order(order):
    records = _read_data()
    order_id = max((record["id"] for record in records), default=0) + 1

    order = Order(id=order_id, **order.model_dump(exclude={"id"}))
    records.append(order.model_dump(mode="json"))
    _write_data(records)

    return order