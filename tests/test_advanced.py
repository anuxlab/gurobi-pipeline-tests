import pytest
import gurobipy as gp

from gurobi_tests.gurobi_env import new_env


@pytest.mark.mip
def test_mip_with_solution_pool():
    env = new_env()
    try:
        m = gp.Model("solution_pool", env=env)
        x = m.addVars(3, vtype=gp.GRB.BINARY)
        m.addConstr(gp.quicksum(x[i] for i in range(3)) == 1)
        m.setObjective(gp.quicksum((i + 1) * x[i] for i in range(3)), gp.GRB.MINIMIZE)
        m.Params.PoolSearchMode = 2
        m.Params.PoolSolutions = 3
        m.optimize()
        assert m.Status == gp.GRB.OPTIMAL
        assert m.SolCount >= 1
    finally:
        env.dispose()


@pytest.mark.smoke
def test_model_parameter_configuration():
    env = new_env()
    try:
        m = gp.Model("parameter_test", env=env)
        m.Params.TimeLimit = 5
        m.Params.MIPGap = 0.01
        m.Params.Threads = 1
        assert m.Params.TimeLimit == 5.0
        assert abs(m.Params.MIPGap - 0.01) < 1e-12
        assert m.Params.Threads == 1
    finally:
        env.dispose()


@pytest.mark.mip
def test_binary_assignment_model():
    env = new_env()
    try:
        m = gp.Model("assignment", env=env)

        costs = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
        x = m.addVars(3, 3, vtype=gp.GRB.BINARY, name="x")

        for i in range(3):
            m.addConstr(gp.quicksum(x[i, j] for j in range(3)) == 1)
        for j in range(3):
            m.addConstr(gp.quicksum(x[i, j] for i in range(3)) == 1)

        m.setObjective(
            gp.quicksum(costs[i][j] * x[i, j] for i in range(3) for j in range(3)),
            gp.GRB.MINIMIZE,
        )
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(m.ObjVal - 3.0) < 1e-7
    finally:
        env.dispose()
