import json

def get_restaurants():
    with open("data/restaurants.json", encoding="utf-8") as file:
        return json.load(file)