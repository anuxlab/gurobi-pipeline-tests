import os
from pathlib import Path

import gurobipy as gp
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "config.yaml"


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def create_environment():
    access_id = os.environ["GRB_WLSACCESSID"]
    secret = os.environ["GRB_WLSSECRET"]
    license_id = int(os.environ["GRB_LICENSEID"])

    env = gp.Env(
        params={
            "WLSACCESSID": access_id,
            "WLSSECRET": secret,
            "LICENSEID": license_id,
        }
    )

    return env


def test_evrp_small_instance():
    """
    Small deterministic EVRP smoke test.

    Verifies:
    - Gurobi WLS works
    - binary routing variables work
    - vehicle capacity constraint works
    - battery/energy constraint works
    - customer service constraint works
    - model reaches an optimal solution
    """

    config = load_config()

    vehicle = config["evrp"]["vehicle"]

    capacity = vehicle["capacity"]
    battery_capacity = vehicle["battery_capacity"]
    energy_rate = vehicle["energy_rate"]

    env = create_environment()

    try:
        model = gp.Model("tiny_evrp", env=env)

        # ----------------------------------------------------
        # Tiny instance
        #
        # 0 = depot
        # 1 = customer 1
        # 2 = customer 2
        # ----------------------------------------------------

        nodes = [0, 1, 2]

        demand = {
            0: 0,
            1: 20,
            2: 20,
        }

        distance = {
            (0, 1): 10,
            (1, 0): 10,
            (0, 2): 15,
            (2, 0): 15,
            (1, 2): 8,
            (2, 1): 8,
        }

        arcs = list(distance.keys())

        # ----------------------------------------------------
        # Decision variables
        # ----------------------------------------------------

        x = model.addVars(
            arcs,
            vtype=gp.GRB.BINARY,
            name="x"
        )

        # ----------------------------------------------------
        # Objective
        # Minimize total distance
        # ----------------------------------------------------

        model.setObjective(
            gp.quicksum(
                distance[i, j] * x[i, j]
                for i, j in arcs
            ),
            gp.GRB.MINIMIZE
        )

        # ----------------------------------------------------
        # Each customer must be visited once
        # ----------------------------------------------------

        for customer in [1, 2]:

            model.addConstr(
                gp.quicksum(
                    x[i, customer]
                    for i in nodes
                    if (i, customer) in x
                ) == 1,
                name=f"visit_{customer}"
            )

            model.addConstr(
                gp.quicksum(
                    x[customer, j]
                    for j in nodes
                    if (customer, j) in x
                ) == 1,
                name=f"leave_{customer}"
            )

        # ----------------------------------------------------
        # Vehicle leaves and returns to depot
        # ----------------------------------------------------

        model.addConstr(
            gp.quicksum(
                x[0, j]
                for j in nodes
                if (0, j) in x
            ) == 1,
            name="depot_departure"
        )

        model.addConstr(
            gp.quicksum(
                x[i, 0]
                for i in nodes
                if (i, 0) in x
            ) == 1,
            name="depot_return"
        )

        # ----------------------------------------------------
        # Capacity
        # ----------------------------------------------------

        total_demand = sum(demand.values())

        assert total_demand <= capacity, (
            "Test instance demand exceeds vehicle capacity"
        )

        # ----------------------------------------------------
        # Energy constraint
        # ----------------------------------------------------

        total_distance = gp.quicksum(
            distance[i, j] * x[i, j]
            for i, j in arcs
        )

        total_energy = energy_rate * total_distance

        model.addConstr(
            total_energy <= battery_capacity,
            name="battery_capacity"
        )

        # ----------------------------------------------------
        # Solve
        # ----------------------------------------------------

        model.optimize()

        # ----------------------------------------------------
        # Assertions
        # ----------------------------------------------------

        assert model.Status == gp.GRB.OPTIMAL

        assert model.SolCount > 0

        # Expected optimal route:
        #
        # 0 -> 1 -> 2 -> 0
        #
        # distance = 10 + 8 + 15 = 33
        #
        expected_distance = 33.0

        assert abs(model.ObjVal - expected_distance) < 1e-6

        # Check battery feasibility
        expected_energy = expected_distance * energy_rate

        assert expected_energy <= battery_capacity

    finally:
        env.close()