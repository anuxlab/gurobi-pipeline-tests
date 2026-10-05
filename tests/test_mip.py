import pytest
import gurobipy as gp

from gurobi_tests.gurobi_env import new_env


@pytest.mark.mip
def test_small_mip():
    env = new_env()
    try:
        m = gp.Model("small_mip", env=env)
        x = m.addVars(4, vtype=gp.GRB.BINARY, name="x")
        values = [10, 8, 7, 6]
        weights = [6, 5, 4, 3]

        m.addConstr(gp.quicksum(weights[i] * x[i] for i in range(4)) <= 10)
        m.setObjective(gp.quicksum(values[i] * x[i] for i in range(4)), gp.GRB.MAXIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(m.ObjVal - 17.0) < 1e-7
    finally:
        env.dispose()


@pytest.mark.mip
def test_integer_constraint():
    env = new_env()
    try:
        m = gp.Model("integer_test", env=env)
        x = m.addVar(vtype=gp.GRB.INTEGER, lb=0, ub=10)
        m.addConstr(3 * x >= 10)
        m.setObjective(x, gp.GRB.MINIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert x.X == 4
    finally:
        env.dispose()


@pytest.mark.mip
def test_infeasible_model_is_detected():
    env = new_env()
    try:
        m = gp.Model("infeasible_test", env=env)
        x = m.addVar(lb=0, ub=1)
        m.addConstr(x >= 2)
        m.optimize()
        assert m.Status == gp.GRB.INFEASIBLE
    finally:
        env.dispose()
