# Drop Chute
>Food delivery project for COSC 310. \
Team Name: Drop Chute


Lab Section:
>L02 - Tuesday 2-4pm \
This repository contains Drop Chute's submission for Milestone 2. The application allows customers to register, sign in, discover restaurants, browse menus, build a shopping cart, and validate it for checkout. It also supports restaurant and menu management for restaurant users and administrators.\
Implemented so far: a FastAPI backend with a layered architecture (Route → Service → Repository → JSON) and a plain HTML/JavaScript frontend that talks to the REST API. Customers can register, sign in with a token, view and update their account and delivery address, and deactivate their account. Account and cart routes are protected by a shared sign-in check that returns 401 for a missing, invalid or expired token and 403 for another customer's account or cart. Carts hold items from one restaurant, with subtotal, tax and total calculated by the backend, and checkout validation re-checks the customer, cart and current menu prices.\

# Setup
## Prerequisites
- Python [Version [3.11.9](https://www.python.org/downloads/)]
- pip
- git


## Installation
1. Clone the repository
```bash
git clone <repo-url>
cd <repo-folder>
```

2. Create and activate a virtual environment
```bash
# Create
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r docs/requirements.txt
```


# Running the Application
```bash
uvicorn app.main:app --reload
```

>The API will be available at **http://127.0.0.1:8000**

### Running Tests
```bash
python -m pytest -v
```
>Note: Use **python -m pytest -v** , not **pytest -v** , to ensure the app package resolves correctly on all setups

### Continuous Integration
GitHub Actions runs the test suite automatically every push and pull request (see .github\workflows)

# API Endpoints

| Method | Path                                              | Description                                                  |
|--------|---------------------------------------------------|--------------------------------------------------------------|
| GET | `/`                                                  | Return the API welcome message                               |
| GET | `/health`                                            | Return the API health status                                 |
| POST | `/auth/login`                                       | Sign in and return an access token                           |
| POST | `/customers`                                        | Register a new customer                                      |
| GET | `/customers/{customer_id}`                           | View your account details                                    |
| PATCH | `/customers/{customer_id}`                         | Update your delivery address                                 |
| POST | `/customers/{customer_id}/deactivate`               | Deactivate your account                                      |
| GET | `/restaurants`                                       | List all restaurants and their menus                         |
| GET | `/restaurants/mine`                                  | List restaurants owned by the signed-in customer             |
| POST | `/CreateRestaurant`                                 | Create a restaurant owned by the signed-in customer          |
| POST | `/restaurants/{restaurant_id}/items`                | Add a menu item to a restaurant you own                      |
| PATCH | `/restaurants/{restaurant_id}`                     | Update a restaurant you own                                  |
| PATCH | `/restaurants/{restaurant_id}/items/{item_name}`   | Update a menu item at a restaurant you own                   |
| GET | `/customers/{customer_id}/cart`                      | Get the customer's active cart                               |
| POST | `/customers/{customer_id}/cart`                     | Create or retrieve the customer's active cart                |
| DELETE | `/customers/{customer_id}/cart`                   | Clear the customer's active cart                             |
| POST | `/customers/{customer_id}/cart/items`               | Add an item to the active cart                               |
| PATCH | `/customers/{customer_id}/cart/items/{item_name}`  | Update a cart item's quantity                                |
| DELETE | `/customers/{customer_id}/cart/items/{item_name}` | Remove an item from the active cart                          |
| POST | `/customers/{customer_id}/checkout/validate`        | Validate the active cart against the current menu and prices |
| POST | `/customers/{customer_id}/orders`                   | Place an order from the active cart                          |
| GET | `/customers/{customer_id}/orders`                    | List the customer's orders                                   |
| GET | `/customers/{customer_id}/orders/{order_id}`         | Get details for a specific order                             |

### Interactive docs
FastAPI provides auto-generated interactive API documentation at: 
**http://127.0.0.1:8000/docs**

### Representative Data
Cart, Customer, Order, and Restaurant data lives at: 
```bash
data/carts.json
data/customers.json
data/orders.json
data/restaurants.json
```

# Repository Structure
```bash
Drop-Chute-310-Food-delivery/
├── .github\workflows
│   └── python-app.yaml
├── app/
│   ├── exceptions.py
│   ├── main.py
│   ├── security.py
│   ├── tokens.py
│   ├── api\routes/
│   │   ├── auth_routes.py
│   │   ├── cart.py
│   │   ├── checkout_routes.py
│   │   ├── dependencies.py
│   │   ├── order_routes.py
│   │   └── restaurants.py
│   ├── repositories/
│   │   ├── cart_repo.py
│   │   ├── customer_repository.py
│   │   ├── order_repo.py
│   │   └── restaurant_repository.py
│   ├── schemas/
│   │   ├── authschema.py
│   │   ├── cart.py
│   │   ├── customerschema.py
│   │   ├── health.py
│   │   ├── home.py
│   │   ├── order.py 
│   │   └── restaurantschemas.py
│   └── services/
│       ├── auth_service.py
│       ├── cart_service.py
│       ├── checkout_service.py
│       ├── customer_services.py
│       ├── order_service.py
│       └── restaurant_services.py
├── data/
│   ├── carts.json
│   ├── customers.json
│   ├── orders.json
│   └── restaurants.json
├── docs/
│   ├── .gitignore
│   ├── PROVENANCE.md
│   ├── README.md
│   ├── requirements.txt
│   └── team-agreement.md
├── frontEnd/
│   ├── Account.html
│   ├── Account.js
│   ├── api.js
│   ├── app.js
│   ├── cart.js
│   ├── checkout.html
│   ├── checkout.js
│   ├── customer.html
│   ├── customer.js
│   ├── index.html
│   ├── login.html
│   ├── login.js
│   ├── order-details.html
│   ├── order-details.js
│   ├── order-history.html
│   ├── order-history.js
│   ├── register.html
│   ├── register.js
│   ├── restaurant-account.html
│   ├── restaurant-account.js
│   ├── restaurant.html
│   ├── restaurant.js
│   └── styles.css
└── tests/
    ├── __pycache__/
    ├── test_auth_routes.py
    ├── Test_cart.py
    ├── test_checkout.py
    ├── test_customer_account_routes.py
    ├── test_customers.py
    ├── test_health.py
    ├── test_orders.py
    ├── test_password_hashing.py
    ├── test_restaurant_ownership.py
    ├── test_resturaunts.py
    ├── test_tokens.py
    └── tests_multiple_sub_tests.py
```
