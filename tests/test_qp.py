import pytest
import gurobipy as gp

from gurobi_tests.gurobi_env import new_env


@pytest.mark.qp
def test_convex_qp():
    env = new_env()
    try:
        m = gp.Model("convex_qp", env=env)
        x = m.addVars(2, lb=-10, ub=10, name="x")
        m.addConstr(x[0] + x[1] >= 1)
        m.setObjective(x[0] * x[0] + x[1] * x[1], gp.GRB.MINIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(m.ObjVal - 0.5) < 1e-6
        assert abs(x[0].X - 0.5) < 1e-6
        assert abs(x[1].X - 0.5) < 1e-6
    finally:
        env.dispose()


@pytest.mark.qp
def test_qp_has_expected_solution_quality():
    env = new_env()
    try:
        m = gp.Model("qp_quality", env=env)
        x = m.addVar(lb=0, ub=10)
        y = m.addVar(lb=0, ub=10)
        m.addConstr(x + y == 4)
        m.setObjective((x - 1) * (x - 1) + (y - 3) * (y - 3), gp.GRB.MINIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(x.X - 1.0) < 1e-6
        assert abs(y.X - 3.0) < 1e-6
        assert abs(m.ObjVal) < 1e-7
    finally:
        env.dispose()
