import gurobipy as gp

def test_parameters_and_counts(solver_env):
    m=gp.Model("advanced", env=solver_env)
    m.Params.OutputFlag=0
    x=m.addVars(3, lb=0, ub=10)
    m.addConstr(x[0]+x[1]+x[2] <= 10)
    m.setObjective(2*x[0]+x[1]+x[2], gp.GRB.MAXIMIZE)
    assert m.NumVars == 3
    assert m.NumConstrs == 1
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    m.dispose()
