from __future__ import annotations

import os

import gurobipy as gp
import pytest

from gurobi_tests.gurobi_env import credentials_from_env


@pytest.mark.smoke
def test_wls_credentials_are_valid_format():
    creds = credentials_from_env()
    assert isinstance(creds["GRB_LICENSEID"], int)
    assert creds["GRB_LICENSEID"] > 0


@pytest.mark.smoke
def test_gurobi_version():
    expected = tuple(map(int, os.getenv("EXPECTED_GUROBI_VERSION", "13.0.3").split(".")))
    assert gp.gurobi.version() == expected


@pytest.mark.smoke
def test_wls_can_start_environment(solver_env):
    model = gp.Model("wls_smoke", env=solver_env)
    x = model.addVar(lb=0, ub=1)
    model.setObjective(x, gp.GRB.MAXIMIZE)
    model.optimize()
    assert model.Status == gp.GRB.OPTIMAL
    assert abs(x.X - 1.0) <= 1e-8
    model.dispose()
