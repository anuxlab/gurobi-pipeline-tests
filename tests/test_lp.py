import pytest
import gurobipy as gp


@pytest.mark.lp
def test_lp_optimal_solution(solver_env):
    m = gp.Model("lp", env=solver_env)
    try:
        x = m.addVars(2, lb=0, name="x")
        m.addConstr(x[0] + x[1] >= 10)
        m.addConstr(2 * x[0] + x[1] >= 14)
        m.setObjective(3 * x[0] + 2 * x[1], gp.GRB.MINIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(m.ObjVal - 24.0) < 1e-7
    finally:
        m.dispose()


@pytest.mark.lp
def test_unbounded_lp(solver_env):
    m = gp.Model("unbounded", env=solver_env)
    try:
        x = m.addVar(lb=0)
        m.setObjective(x, gp.GRB.MAXIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.UNBOUNDED
    finally:
        m.dispose()
