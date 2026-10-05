import os
import pytest
import gurobipy as gp

from gurobi_tests.gurobi_env import credentials_from_env, new_env


@pytest.mark.smoke
def test_gurobi_python_version():
    assert gp.gurobi.version() == (13, 0, 3)


@pytest.mark.smoke
def test_wls_credentials_are_present():
    credentials_from_env()


@pytest.mark.smoke
def test_wls_license_can_create_model():
    env = new_env()
    try:
        model = gp.Model("license_smoke", env=env)
        x = model.addVar(lb=0, ub=1, name="x")
        model.setObjective(x, gp.GRB.MAXIMIZE)
        model.optimize()
        assert model.Status == gp.GRB.OPTIMAL
        assert abs(x.X - 1.0) < 1e-8
    finally:
        env.dispose()
