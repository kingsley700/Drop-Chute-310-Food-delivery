# Drop Chute
>Food delivery project for COSC 310. \
Team Name: Drop Chute


Lab Section:
>L02 - Tuesday 2-4pm \
This repository contains Drop Chute's submission for Milestone 0. The application allows customers to discover restaurants, browse items, and place orders. It supports restaurant and platform management for restaurant users and administrators.


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

# API Endpoints

|Method|Path        |Description                           |
|------|------------|--------------------------------------|
|GET   |/           |Welcome message                       |
|GET   |/health     |Health check, returns {"status": "Ok"}|
|GET   |/restaurants|Return list of all restaurants        |

### Interactive docs
FastAPI provides auto-generated interactive API documentation at: 
**http://127.0.0.1:8000/docs**

### Representative Data
Sample restaurant data lives at: 
```bash
data/restaurants.json
```
Where it is read by **app/repositories/restaurant_repository.py** and served through **/restaurants.**

# Repository Structure
```bash
Drop-Chute-310-Food-delivery/
├── app/
│   ├── main.py
│   ├── api\routes/
│   │   └── restaurants.py
│   ├── repositories/
│   │   └── restaurant_repository.py
│   ├── schemas/
│   │   └── restaurant.py
│   └── services/
│       └── restaurant_services.py
├── data/
│   └── restaurants.json
├── docs/
│   ├── .gitignore
│   ├── README.md
│   ├── requirements.txt
│   └── team-agreement.md
└── tests/
    ├── test_health.py
    └── test_restaurants.py
```
