import pytest
import gurobipy as gp


@pytest.mark.advanced
def test_parameter_roundtrip(solver_env):
    m = gp.Model("parameters", env=solver_env)
    m.Params.TimeLimit = 5
    m.Params.MIPGap = 0.01
    m.Params.Threads = 1
    assert m.Params.TimeLimit == 5.0
    assert abs(m.Params.MIPGap - 0.01) < 1e-12
    assert m.Params.Threads == 1
    m.dispose()


@pytest.mark.advanced
def test_solution_pool(solver_env):
    m = gp.Model("solution_pool", env=solver_env)
    x = m.addVars(3, vtype=gp.GRB.BINARY)
    m.addConstr(gp.quicksum(x[i] for i in range(3)) == 1)
    m.setObjective(gp.quicksum((i+1)*x[i] for i in range(3)), gp.GRB.MINIMIZE)
    m.Params.PoolSearchMode = 2
    m.Params.PoolSolutions = 3
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert m.SolCount >= 3
    assert abs(m.PoolObjVal - 1.0) < 1e-8
    m.dispose()


@pytest.mark.advanced
def test_model_counts_and_write(solver_env, tmp_path):
    m = gp.Model("counts", env=solver_env)
    x = m.addVars(5, vtype=gp.GRB.BINARY)
    m.addConstr(gp.quicksum(x) <= 2)
    m.setObjective(gp.quicksum(x), gp.GRB.MAXIMIZE)
    m.update()
    assert m.NumVars == 5
    assert m.NumConstrs == 1
    path = tmp_path / "model.lp"
    m.write(str(path))
    assert path.exists() and path.stat().st_size > 0
    m.dispose()
