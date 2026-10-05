import os
import pytest
import gurobipy as gp

from gurobi_tests.config import instance_path
from gurobi_tests.evrp_model import build_evrp_model, load_instance
from gurobi_tests.gurobi_env import new_env


INSTANCE = os.getenv("EVRP_INSTANCE", "tiny_evrp.json")


@pytest.mark.evrp
def test_evrp_instance_solves():
    path = instance_path(INSTANCE)
    assert path.exists(), f"Missing EVRP instance: {path}"

    data = load_instance(path)
    env = new_env()
    try:
        m, vars_ = build_evrp_model(env, data)
        m.Params.TimeLimit = 30
        m.Params.MIPGap = 0.0
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL, (
            f"{INSTANCE}: expected OPTIMAL, got status {m.Status}"
        )
        assert m.SolCount >= 1
        assert m.ObjVal >= 0
    finally:
        env.dispose()
