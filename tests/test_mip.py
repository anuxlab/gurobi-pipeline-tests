import os

import gurobipy as gp


def create_environment():
    """Create a Gurobi environment using WLS credentials."""

    return gp.Env(
        params={
            "WLSACCESSID": os.environ["GRB_WLSACCESSID"],
            "WLSSECRET": os.environ["GRB_WLSSECRET"],
            "LICENSEID": int(os.environ["GRB_LICENSEID"]),
        }
    )


def test_binary_mip():
    """
    Test a simple binary MILP.

    max 3x + 2y

    subject to:
        x + y <= 1
        x,y ∈ {0,1}

    Expected:
        x = 1
        y = 0
        objective = 3
    """

    env = create_environment()

    try:
        model = gp.Model("binary_mip_test", env=env)

        x = model.addVar(vtype=gp.GRB.BINARY, name="x")
        y = model.addVar(vtype=gp.GRB.BINARY, name="y")

        model.addConstr(
            x + y <= 1,
            name="capacity"
        )

        model.setObjective(
            3 * x + 2 * y,
            gp.GRB.MAXIMIZE
        )

        model.optimize()

        assert model.Status == gp.GRB.OPTIMAL
        assert model.SolCount > 0

        assert abs(x.X - 1.0) < 1e-6
        assert abs(y.X - 0.0) < 1e-6
        assert abs(model.ObjVal - 3.0) < 1e-6

    finally:
        env.close()


def test_integer_mip():
    """
    Test an integer optimization problem.

    max 7x

    subject to:
        2x <= 10
        x >= 0
        x ∈ Z

    Expected:
        x = 5
        objective = 35
    """

    env = create_environment()

    try:
        model = gp.Model("integer_mip_test", env=env)

        x = model.addVar(
            vtype=gp.GRB.INTEGER,
            lb=0,
            name="x"
        )

        model.addConstr(
            2 * x <= 10,
            name="upper_bound"
        )

        model.setObjective(
            7 * x,
            gp.GRB.MAXIMIZE
        )

        model.optimize()

        assert model.Status == gp.GRB.OPTIMAL
        assert model.SolCount > 0

        assert abs(x.X - 5.0) < 1e-6
        assert abs(model.ObjVal - 35.0) < 1e-6

    finally:
        env.close()


def test_mip_multiple_constraints():
    """
    Test a small binary knapsack problem.

    Items:
        A: value=10, weight=4
        B: value=7,  weight=3
        C: value=6,  weight=2

    Capacity = 5

    Optimal solution:
        A + C
        value = 16
        weight = 6 -> infeasible

    Therefore the optimal feasible solution is:
        B + C
        value = 13
        weight = 5
    """

    env = create_environment()

    try:
        model = gp.Model("knapsack_test", env=env)

        x_a = model.addVar(vtype=gp.GRB.BINARY, name="A")
        x_b = model.addVar(vtype=gp.GRB.BINARY, name="B")
        x_c = model.addVar(vtype=gp.GRB.BINARY, name="C")

        model.addConstr(
            4 * x_a + 3 * x_b + 2 * x_c <= 5,
            name="capacity"
        )

        model.setObjective(
            10 * x_a + 7 * x_b + 6 * x_c,
            gp.GRB.MAXIMIZE
        )

        model.optimize()

        assert model.Status == gp.GRB.OPTIMAL

        assert abs(x_a.X - 0.0) < 1e-6
        assert abs(x_b.X - 1.0) < 1e-6
        assert abs(x_c.X - 1.0) < 1e-6

        assert abs(model.ObjVal - 13.0) < 1e-6

    finally:
        env.close()


def test_infeasible_mip():
    """
    Test Gurobi's handling of an infeasible MILP.

    x >= 10
    x <= 5
    """

    env = create_environment()

    try:
        model = gp.Model("infeasible_mip_test", env=env)

        x = model.addVar(
            vtype=gp.GRB.INTEGER,
            name="x"
        )

        model.addConstr(
            x >= 10,
            name="lower"
        )

        model.addConstr(
            x <= 5,
            name="upper"
        )

        model.optimize()

        assert model.Status == gp.GRB.INFEASIBLE

    finally:
        env.close()