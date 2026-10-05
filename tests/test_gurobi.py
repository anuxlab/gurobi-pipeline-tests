import pytest
import gurobipy as gp


@pytest.mark.smoke
def test_gurobi_version():
    assert gp.gurobi.version() == (13, 0, 3)


@pytest.mark.smoke
def test_wls_environment_starts(solver_env):
    model = gp.Model("wls_smoke", env=solver_env)
    try:
        x = model.addVar(lb=0, ub=1, name="x")
        model.setObjective(x, gp.GRB.MAXIMIZE)
        model.optimize()

        assert model.Status == gp.GRB.OPTIMAL
        assert model.SolCount == 1
        assert abs(x.X - 1.0) < 1e-8
    finally:
        model.dispose()
