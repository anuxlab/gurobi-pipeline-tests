import pytest
import gurobipy as gp

from gurobi_tests.gurobi_env import new_env


@pytest.mark.lp
def test_small_lp():
    env = new_env()
    try:
        m = gp.Model("small_lp", env=env)
        x = m.addVars(2, lb=0, name="x")
        m.addConstr(x[0] + x[1] >= 10)
        m.addConstr(2 * x[0] + x[1] >= 14)
        m.setObjective(3 * x[0] + 2 * x[1], gp.GRB.MINIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(m.ObjVal - 24.0) < 1e-7
    finally:
        env.dispose()
