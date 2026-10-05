import gurobipy as gp

def test_lp(solver_env):
    m = gp.Model("lp", env=solver_env)
    x = m.addVar(lb=0)
    y = m.addVar(lb=0)
    m.addConstr(2*x + y <= 8)
    m.addConstr(x + 2*y <= 8)
    m.setObjective(3*x + 2*y, gp.GRB.MAXIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(m.ObjVal - 13.3333333333) < 1e-6
    m.dispose()
