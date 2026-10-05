import gurobipy as gp

def test_knapsack_mip(solver_env):
    m = gp.Model("knapsack", env=solver_env)
    values=[10,7,6,5]
    weights=[4,3,2,3]
    x=m.addVars(4,vtype=gp.GRB.BINARY)
    m.addConstr(gp.quicksum(weights[i]*x[i] for i in range(4)) <= 7)
    m.setObjective(gp.quicksum(values[i]*x[i] for i in range(4)), gp.GRB.MAXIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(m.ObjVal-18) < 1e-8
    m.dispose()

def test_infeasible_mip(solver_env):
    m=gp.Model("infeasible", env=solver_env)
    x=m.addVar(vtype=gp.GRB.BINARY)
    m.addConstr(x >= 1)
    m.addConstr(x <= 0)
    m.optimize()
    assert m.Status == gp.GRB.INFEASIBLE
    m.dispose()
