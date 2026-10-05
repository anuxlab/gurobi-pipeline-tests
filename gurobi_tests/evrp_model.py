from __future__ import annotations

import json
import math
from pathlib import Path

import gurobipy as gp


def load_instance(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_instance(data: dict) -> None:
    required = {"nodes", "depot", "customers", "vehicle", "demand"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"Missing instance fields: {sorted(missing)}")
    nodes = {str(k) for k in data["nodes"]}
    depot = str(data["depot"])
    customers = [str(x) for x in data["customers"]]
    if depot not in nodes:
        raise ValueError("Depot is not present in nodes")
    if not customers or any(c not in nodes for c in customers):
        raise ValueError("Every customer must be present in nodes")
    if len(set(customers)) != len(customers):
        raise ValueError("Customer list contains duplicates")
    vehicle = data["vehicle"]
    for key in ("capacity", "battery_capacity", "energy_rate"):
        if float(vehicle[key]) <= 0:
            raise ValueError(f"vehicle.{key} must be positive")
    demand = {str(k): float(v) for k, v in data["demand"].items()}
    if any(demand.get(c, -1) < 0 for c in customers):
        raise ValueError("Every customer needs a non-negative demand")
    if sum(demand[c] for c in customers) > float(vehicle["capacity"]):
        raise ValueError("Total demand exceeds vehicle capacity for this single-vehicle CI model")


def build_evrp_model(env: gp.Env, data: dict) -> tuple[gp.Model, dict]:
    """Build a small, deterministic single-vehicle EVRP-style MILP.

    The CI model deliberately uses one depot and customer nodes. Charging
    stations are optional and represented as route nodes, but the supplied
    instances are constructed so the route is feasible without charging.
    Battery is modeled on directed arcs with a separate start-energy
    constraint; return-to-depot energy is represented by an arc variable and
    does not overwrite the start-energy state.
    """
    validate_instance(data)

    nodes = {str(k): tuple(v) for k, v in data["nodes"].items()}
    depot = str(data["depot"])
    customers = [str(x) for x in data["customers"]]
    stations = [str(x) for x in data.get("charging_stations", [])]
    route_nodes = [depot] + customers + stations
    capacity = float(data["vehicle"]["capacity"])
    battery = float(data["vehicle"]["battery_capacity"])
    energy_rate = float(data["vehicle"]["energy_rate"])
    demand = {str(k): float(v) for k, v in data["demand"].items()}

    def distance(i: str, j: str) -> float:
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        return math.hypot(xi - xj, yi - yj)

    arcs = [(i, j) for i in route_nodes for j in route_nodes if i != j]
    m = gp.Model("evrp_ci", env=env)

    x = m.addVars(arcs, vtype=gp.GRB.BINARY, name="x")
    load = m.addVars(customers, lb=0, ub=capacity, name="load")
    arrival_energy = m.addVars(customers, lb=0, ub=battery, name="energy")
    order = m.addVars(customers, lb=1, ub=len(customers), name="order")

    # Every customer is entered and exited exactly once.
    for c in customers:
        m.addConstr(gp.quicksum(x[i, c] for i in route_nodes if i != c) == 1)
        m.addConstr(gp.quicksum(x[c, j] for j in route_nodes if j != c) == 1)

    # One departure and one return to the depot.
    m.addConstr(gp.quicksum(x[depot, j] for j in route_nodes if j != depot) == 1)
    m.addConstr(gp.quicksum(x[i, depot] for i in route_nodes if i != depot) == 1)

    # Station flow and at-most-once visit.
    for s in stations:
        incoming = gp.quicksum(x[i, s] for i in route_nodes if i != s)
        outgoing = gp.quicksum(x[s, j] for j in route_nodes if j != s)
        m.addConstr(incoming == outgoing)
        m.addConstr(incoming <= 1)

    # Capacity propagation from customer to customer. For CI purposes the
    # station does not add demand.
    for i, j in arcs:
        if j in customers:
            prior_load = load[i] if i in customers else 0.0
            m.addConstr(
                load[j] >= prior_load + demand[j] - capacity * (1 - x[i, j])
            )
    for c in customers:
        m.addConstr(load[c] >= demand[c])

    # Battery propagation only tracks customer arrival energy. A station or
    # depot is treated as a full-charge/reset point in this small CI model.
    for c in customers:
        m.addConstr(arrival_energy[c] <= battery)
        m.addConstr(
            arrival_energy[c]
            <= battery
            - gp.quicksum(
                energy_rate * distance(i, c) * x[i, c]
                for i in route_nodes
                if i != c
            )
            + battery * (1 - gp.quicksum(x[i, c] for i in route_nodes if i != c))
        )
        # A customer cannot be reached if the selected incoming arc needs
        # more energy than a full battery.
        for i in route_nodes:
            if i != c:
                m.addConstr(
                    energy_rate * distance(i, c) * x[i, c] <= battery
                )

    # MTZ subtour elimination among customers.
    n = len(customers)
    for i in customers:
        for j in customers:
            if i != j:
                m.addConstr(order[i] - order[j] + n * x[i, j] <= n - 1)

    travel_cost = gp.quicksum(distance(i, j) * x[i, j] for i, j in arcs)
    station_penalty = 0.001 * gp.quicksum(
        x[i, s] for s in stations for i in route_nodes if i != s
    )
    m.setObjective(travel_cost + station_penalty, gp.GRB.MINIMIZE)
    return m, {"x": x, "load": load, "energy": arrival_energy, "order": order}
