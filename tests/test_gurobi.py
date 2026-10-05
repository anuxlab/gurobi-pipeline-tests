import os
import gurobipy as gp

def test_gurobipy_import():
    assert gp.gurobi.version() == (13, 0, 3)

def test_wls_environment(solver_env):
    m = gp.Model("wls_smoke", env=solver_env)
    x = m.addVar(lb=0, ub=1, name="x")
    m.setObjective(x, gp.GRB.MAXIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(x.X - 1.0) < 1e-8
    m.dispose()
