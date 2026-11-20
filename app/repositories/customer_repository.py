import json
from app.schemas.customerschema import Customer

filep = "data/customers.json"


def _read_data():
    """Reads customers from JSON file."""
    with open(filep, "r", encoding="utf-8") as file:
        text = file.read().strip()
    if text == "":
        return []
    return json.loads(text)


def _write_data(customers):
    """Writes customers to json file."""
    with open(filep, "w", encoding="utf-8") as file:
        json.dump(customers, file, indent=2)


def _next_id(customers):
    """Returns the next unused customer id"""
    highest = 0
    for customer in customers:
        if customer["id"] > highest:
            highest = customer["id"]
    return highest + 1


def get_customers():
    """Returns all customers as Customer objects"""
    customers = []
    for record in _read_data():
        customers.append(Customer(**record))
    return customers


def get_customer_by_id(customer_id: int):
    """Returns customer based on ID"""
    for customer in get_customers():
        if customer.id == customer_id:
            return customer
    return None


def get_customer_by_email(customer_email: str):
    """Returns a customer based on email"""
    for customer in get_customers():
        if customer.email.lower() == customer_email.strip().lower():
            return customer
    return None


def create_customer(name, email, hashed_password, delivery_address):
    """Saves a new customer and returns"""
    records = _read_data()
    customer = Customer(
        id=_next_id(records),
        name=name,
        email=email,
        hashed_password=hashed_password,
        delivery_address=delivery_address,
    )
    records.append(customer.model_dump())
    _write_data(records)
    return customer

def update_customer_address(customer_id: int, delivery_address: str):
    """Changes a customer's delivery address and returns the updated customer, or None if not found."""
    records = _read_data()
    for record in records:
        if record["id"] == customer_id:
            record["delivery_address"] = delivery_address
            _write_data(records)
            return Customer(**record)
    return None

def deactivate_customer(customer_id: int):
    """Marks a customer inactive (the record is kept) and returns it, or None if not found."""
    records = _read_data()
    for record in records:
        if record["id"] == customer_id:
            record["is_active"] = False
            _write_data(records)
            return Customer(**record)
    return None