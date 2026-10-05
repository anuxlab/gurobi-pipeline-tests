import pytest
import gurobipy as gp


@pytest.mark.qp
def test_convex_qp(solver_env):
    m = gp.Model("convex_qp", env=solver_env)
    x = m.addVars(2, lb=-10, ub=10)
    m.addConstr(x[0] + x[1] >= 1)
    m.setObjective(x[0]*x[0] + x[1]*x[1], gp.GRB.MINIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(m.ObjVal - 0.5) < 1e-6
    m.dispose()


@pytest.mark.qp
def test_qp_with_equality(solver_env):
    m = gp.Model("qp_equality", env=solver_env)
    x = m.addVar(lb=0, ub=10)
    y = m.addVar(lb=0, ub=10)
    m.addConstr(x+y == 4)
    m.setObjective((x-1)*(x-1)+(y-3)*(y-3), gp.GRB.MINIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(x.X-1) < 1e-6 and abs(y.X-3) < 1e-6
    m.dispose()
