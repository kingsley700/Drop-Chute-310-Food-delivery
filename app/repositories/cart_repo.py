
import json
from app.schemas.cart import Cart

filep = "data/carts.json"


def _read_data():
    """Reads carts from JSON file."""
    with open(filep, "r", encoding="utf-8") as file:
        text = file.read().strip()
    if text == "":
        return []
    return json.loads(text)


def _write_data(carts):
    """Writes carts to JSON file."""
    with open(filep, "w", encoding="utf-8") as file:
        json.dump(carts, file, indent=2)


def _next_id(carts):
    """Returns the next unused cart id."""
    highest = 0
    for cart in carts:
        if cart["id"] > highest:
            highest = cart["id"]
    return highest + 1


def get_cart_by_customer(customer_id: int):
    """Returns the customer's active cart."""
    for cart in get_carts():
        if cart.customer_id == customer_id and cart.status == "active":
            return cart
    return None


def get_carts():
    """Returns all carts as Cart objects."""
    carts = []
    for record in _read_data():
        carts.append(Cart(**record))
    return carts


def create_cart(customer_id: int):
    """Creates a new cart and returns it."""
    records = _read_data()

    cart = Cart(id=_next_id(records),customer_id=customer_id,status="active")

    records.append(cart.model_dump())
    _write_data(records)

    return cart

def update_cart(cart):
    """Updates a cart."""
    carts = _read_data()

    for index, record in enumerate(carts):
        if record["id"] == cart.id:
            carts[index] = cart.model_dump()
            _write_data(carts)
            return cart

    return None