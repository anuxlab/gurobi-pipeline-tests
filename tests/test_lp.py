import pytest
import gurobipy as gp


@pytest.mark.lp
def test_small_lp(solver_env):
    m = gp.Model("small_lp", env=solver_env)
    x = m.addVars(2, lb=0)
    m.addConstr(x[0] + x[1] >= 10)
    m.addConstr(2*x[0] + x[1] >= 14)
    m.setObjective(3*x[0] + 2*x[1], gp.GRB.MINIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(m.ObjVal - 24.0) < 1e-7
    m.dispose()


@pytest.mark.lp
def test_unbounded_lp_status(solver_env):
    m = gp.Model("unbounded_lp", env=solver_env)
    x = m.addVar(lb=-gp.GRB.INFINITY)
    m.setObjective(x, gp.GRB.MINIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.UNBOUNDED
    m.dispose()
