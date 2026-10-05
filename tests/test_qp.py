import gurobipy as gp

def test_convex_qp(solver_env):
    m=gp.Model("qp", env=solver_env)
    x=m.addVar()
    y=m.addVar()
    m.addConstr(x+y >= 1)
    m.setObjective(x*x+y*y, gp.GRB.MINIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(m.ObjVal-0.5) < 1e-6
    m.dispose()
