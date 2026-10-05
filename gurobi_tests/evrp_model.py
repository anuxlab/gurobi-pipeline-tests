from __future__ import annotations

import json
import math
from pathlib import Path

import gurobipy as gp


def load_instance(path: str | Path) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_instance(data: dict) -> None:
    required = {"name", "depot", "customers", "nodes", "demand", "vehicle"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"Missing instance fields: {sorted(missing)}")

    depot = str(data["depot"])
    nodes = {str(k): v for k, v in data["nodes"].items()}
    customers = [str(c) for c in data["customers"]]
    stations = [str(s) for s in data.get("charging_stations", [])]

    if depot not in nodes:
        raise ValueError("Depot is not present in nodes.")
    if len(customers) != len(set(customers)):
        raise ValueError("Customer IDs must be unique.")
    if not customers:
        raise ValueError("At least one customer is required.")
    if set(customers) & set(stations):
        raise ValueError("A node cannot be both customer and charging station.")

    for node_id, point in nodes.items():
        if not isinstance(point, dict) or not {"x", "y"} <= set(point):
            raise ValueError(f"Node {node_id} must contain numeric x/y coordinates.")
        float(point["x"])
        float(point["y"])

    demand = {str(k): float(v) for k, v in data["demand"].items()}
    for customer in customers:
        if customer not in demand:
            raise ValueError(f"Missing demand for customer {customer}")
        if demand[customer] < 0:
            raise ValueError(f"Negative demand for customer {customer}")

    vehicle = data["vehicle"]
    capacity = float(vehicle["capacity"])
    battery = float(vehicle["battery_capacity"])
    if capacity <= 0 or battery <= 0:
        raise ValueError("Vehicle capacity and battery capacity must be positive.")


def build_routing_model(env: gp.Env, data: dict) -> tuple[gp.Model, dict]:
    validate_instance(data)

    depot = str(data["depot"])
    customers = [str(c) for c in data["customers"]]
    nodes = {str(k): v for k, v in data["nodes"].items()}
    vehicle = data["vehicle"]
    capacity = float(vehicle["capacity"])
    battery = float(vehicle["battery_capacity"])
    energy_rate = float(vehicle.get("energy_rate", 1.0))

    route_nodes = [depot] + customers

    def distance(i: str, j: str) -> float:
        dx = float(nodes[i]["x"]) - float(nodes[j]["x"])
        dy = float(nodes[i]["y"]) - float(nodes[j]["y"])
        return math.hypot(dx, dy)

    arcs = [(i, j) for i in route_nodes for j in route_nodes if i != j]
    m = gp.Model(f"evrp_{data['name']}", env=env)

    x = m.addVars(arcs, vtype=gp.GRB.BINARY, name="x")
    load = m.addVars(route_nodes, lb=0, ub=capacity, name="load")
    order = m.addVars(customers, lb=1, ub=len(customers), name="order")

    for customer in customers:
        m.addConstr(
            gp.quicksum(x[i, customer] for i in route_nodes if i != customer) == 1,
            name=f"enter_{customer}",
        )
        m.addConstr(
            gp.quicksum(x[customer, j] for j in route_nodes if j != customer) == 1,
            name=f"leave_{customer}",
        )

    m.addConstr(
        gp.quicksum(x[depot, j] for j in customers) == 1,
        name="depot_departure",
    )
    m.addConstr(
        gp.quicksum(x[i, depot] for i in customers) == 1,
        name="depot_return",
    )
    m.addConstr(load[depot] == 0, name="depot_load")

    demand = {str(k): float(v) for k, v in data["demand"].items()}

    for customer in customers:
        m.addConstr(
            load[customer] >= demand[customer],
            name=f"demand_{customer}",
        )

    for i, j in arcs:
        if j in customers:
            m.addConstr(
                load[j] >= load[i] + demand[j] - capacity * (1 - x[i, j]),
                name=f"load_{i}_{j}",
            )

    # MTZ subtour elimination.
    n = len(customers)
    for i in customers:
        for j in customers:
            if i != j:
                m.addConstr(
                    order[i] - order[j] + n * x[i, j] <= n - 1,
                    name=f"mtz_{i}_{j}",
                )

    total_distance = gp.quicksum(
        distance(i, j) * x[i, j] for i, j in arcs
    )
    total_energy = energy_rate * total_distance

    m.addConstr(
        total_energy <= battery,
        name="route_energy_budget",
    )

    m.setObjective(total_distance, gp.GRB.MINIMIZE)

    return m, {"x": x, "load": load, "order": order}
