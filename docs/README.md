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
```{r}
git clone <repo-url>
cd <repo-folder>
```

2. Create and activate a virtual environment
```{r}
# Create
python -m venv .venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

3. Install dependencies
```{r}
pip install -r requirements.txt
```

# Running the Application
```{r}
uvicorn app.main:app --reload
```

#### Team Members:
Vassilios Simeonidis\
Chance Dreyer\
Teppei Onishi\
Rayan Cooper

