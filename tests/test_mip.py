import pytest
import gurobipy as gp


@pytest.mark.mip
def test_knapsack_mip(solver_env):
    m = gp.Model("knapsack", env=solver_env)
    x = m.addVars(4, vtype=gp.GRB.BINARY)
    values = [10, 8, 7, 6]
    weights = [6, 5, 4, 3]
    m.addConstr(gp.quicksum(weights[i]*x[i] for i in range(4)) <= 10)
    m.setObjective(gp.quicksum(values[i]*x[i] for i in range(4)), gp.GRB.MAXIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(m.ObjVal - 17.0) < 1e-7
    m.dispose()


@pytest.mark.mip
def test_assignment_mip(solver_env):
    m = gp.Model("assignment", env=solver_env)
    costs = [[4,1,3],[2,0,5],[3,2,2]]
    x = m.addVars(3,3,vtype=gp.GRB.BINARY)
    for i in range(3): m.addConstr(gp.quicksum(x[i,j] for j in range(3)) == 1)
    for j in range(3): m.addConstr(gp.quicksum(x[i,j] for i in range(3)) == 1)
    m.setObjective(gp.quicksum(costs[i][j]*x[i,j] for i in range(3) for j in range(3)), gp.GRB.MINIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(m.ObjVal - 5.0) < 1e-7
    m.dispose()


@pytest.mark.mip
def test_integer_model(solver_env):
    m = gp.Model("integer", env=solver_env)
    x = m.addVar(vtype=gp.GRB.INTEGER, lb=0, ub=10)
    m.addConstr(3*x >= 10)
    m.setObjective(x, gp.GRB.MINIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert abs(x.X - 4) < 1e-8
    m.dispose()


@pytest.mark.mip
def test_infeasible_status(solver_env):
    m = gp.Model("infeasible", env=solver_env)
    x = m.addVar(lb=0, ub=1)
    m.addConstr(x >= 2)
    m.optimize()
    assert m.Status == gp.GRB.INFEASIBLE
    m.dispose()
