import json
from pathlib import Path
import gurobipy as gp


def load_instance(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def build_evrp_model(env: gp.Env, data: dict) -> tuple[gp.Model, dict]:
    # Small CI-oriented EVRP-style model:
    # - one depot
    # - customer visits
    # - optional charging station
    # - vehicle capacity
    # - battery/energy feasibility
    # - MTZ subtour elimination
    #
    # This intentionally focuses on exercising Gurobi model construction and
    # optimization rather than reproducing a full thesis formulation.

    nodes = data["nodes"]
    depot = str(data["depot"])
    customers = [str(x) for x in data["customers"]]
    stations = [str(x) for x in data.get("charging_stations", [])]
    route_nodes = [depot] + customers + stations
    vehicle_capacity = float(data["vehicle"]["capacity"])
    battery = float(data["vehicle"]["battery_capacity"])
    energy_rate = float(data["vehicle"]["energy_rate"])

    coords = {str(k): tuple(v) for k, v in nodes.items()}
    demand = {str(k): float(v) for k, v in data.get("demand", {}).items()}

    def dist(i, j):
        xi, yi = coords[i]
        xj, yj = coords[j]
        return ((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5

    arcs = []
    for i in route_nodes:
        for j in route_nodes:
            if i == j:
                continue
            if j == depot and i == depot:
                continue
            arcs.append((i, j))

    m = gp.Model("evrp_ci", env=env)
    x = m.addVars(arcs, vtype=gp.GRB.BINARY, name="x")
    load = m.addVars(route_nodes, lb=0, ub=vehicle_capacity, name="load")
    energy = m.addVars(route_nodes, lb=0, ub=battery, name="energy")
    order = m.addVars(customers, lb=1, ub=len(customers), name="order")

    # Each customer is visited exactly once.
    for c in customers:
        m.addConstr(gp.quicksum(x[i, c] for i in route_nodes if i != c) == 1)
        m.addConstr(gp.quicksum(x[c, j] for j in route_nodes if j != c) == 1)

    # At most one visit to a charging station in these CI instances.
    for s in stations:
        m.addConstr(gp.quicksum(x[i, s] for i in route_nodes if i != s) <= 1)
        m.addConstr(gp.quicksum(x[s, j] for j in route_nodes if j != s) <= 1)

    # Depot start/end.
    m.addConstr(gp.quicksum(x[depot, j] for j in route_nodes if j != depot) == 1)
    m.addConstr(gp.quicksum(x[i, depot] for i in route_nodes if i != depot) == 1)

    # Flow conservation at stations.
    for s in stations:
        m.addConstr(
            gp.quicksum(x[i, s] for i in route_nodes if i != s)
            == gp.quicksum(x[s, j] for j in route_nodes if j != s)
        )

    # Capacity propagation.
    for i, j in arcs:
        if j in customers:
            m.addConstr(
                load[j] >= load[i] + demand.get(j, 0) - vehicle_capacity * (1 - x[i, j])
            )
        else:
            m.addConstr(load[j] >= load[i] - vehicle_capacity * (1 - x[i, j]))

    for c in customers:
        m.addConstr(load[c] >= demand[c])

    m.addConstr(load[depot] == 0)

    # Battery propagation. Charging station resets energy to full when visited.
    for i, j in arcs:
        travel_energy = energy_rate * dist(i, j)
        if j in stations:
            m.addConstr(
                energy[j] >= battery - battery * (1 - x[i, j])
            )
        else:
            m.addConstr(
                energy[j] <= energy[i] - travel_energy + battery * (1 - x[i, j])
            )
            m.addConstr(
                energy[j] >= energy[i] - travel_energy - battery * (1 - x[i, j])
            )

    m.addConstr(energy[depot] == battery)

    # MTZ: prevent customer-only subtours.
    n = len(customers)
    for i in customers:
        for j in customers:
            if i != j:
                m.addConstr(order[i] - order[j] + n * x[i, j] <= n - 1)

    # Minimize travel distance, with a tiny preference against unnecessary station use.
    objective = gp.quicksum(dist(i, j) * x[i, j] for i, j in arcs)
    objective += 0.001 * gp.quicksum(x[i, s] for s in stations for i in route_nodes if i != s)
    m.setObjective(objective, gp.GRB.MINIMIZE)

    return m, {"x": x, "load": load, "energy": energy, "order": order}
