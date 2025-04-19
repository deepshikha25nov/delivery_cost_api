from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
import uvicorn

app = FastAPI()

CENTER_PRODUCTS = {
    "C1": ["A", "B", "C"],
    "C2": ["D", "E", "F"],
    "C3": ["G", "H", "I"]
}

COSTS = {
    ("C1", "L1"): 10,
    ("C2", "L1"): 15,
    ("C3", "L1"): 12,
    ("C1", "C2"): 8,
    ("C2", "C1"): 8,
    ("C2", "C3"): 6,
    ("C3", "C2"): 6,
    ("C1", "C3"): 9,
    ("C3", "C1"): 9
}

class Order(BaseModel):
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0
    E: int = 0
    F: int = 0
    G: int = 0
    H: int = 0
    I: int = 0

def get_required_centers(order: Dict[str, int]) -> set:
    centers_needed = set()
    for product, qty in order.items():
        if qty > 0:
            for center, products in CENTER_PRODUCTS.items():
                if product in products:
                    centers_needed.add(center)
    return centers_needed

from itertools import permutations

def calculate_min_cost(order: Dict[str, int]) -> int:
    centers_needed = get_required_centers(order)
    min_total_cost = float('inf')

    for origin in centers_needed:
        others = centers_needed - {origin}
        routes = permutations(others)
        
        for route in routes:
            path = [origin] + list(route) + ["L1"]
            visited = set()
            total_cost = 0
            current = origin
            carried_weight = 0

            for node in path:
                if node != "L1":
                    for product in CENTER_PRODUCTS[node]:
                        carried_weight += order.get(product, 0) * 0.5
                    visited.add(node)
                if current != node:
                    total_cost += COSTS[(current, node)]
                if node == "L1":
                    carried_weight = 0
                current = node

            min_total_cost = min(min_total_cost, total_cost)

    return min_total_cost

@app.post("/calculate-cost")
async def calculate_delivery_cost(order: Order):
    order_dict = order.dict()
    cost = calculate_min_cost(order_dict)
    return {"minimum_cost": cost}
