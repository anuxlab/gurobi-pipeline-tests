from __future__ import annotations

import pytest
import gurobipy as gp

from gurobi_tests.config import instance_path, load_config
from gurobi_tests.evrp_model import build_evrp_model, load_instance, validate_instance


@pytest.mark.evrp
def test_evrp_instance_schema(evrp_instance):
    path = instance_path(evrp_instance)
    assert path.exists(), f"Missing EVRP instance: {path}"
    data = load_instance(path)
    validate_instance(data)


@pytest.mark.evrp
def test_evrp_instance_solves(evrp_instance, solver_env):
    path = instance_path(evrp_instance)
    assert path.exists(), f"Missing EVRP instance: {path}"
    data = load_instance(path)
    model, variables = build_evrp_model(solver_env, data)
    cfg = load_config()
    gcfg = cfg.get("gurobi", {})
    model.Params.TimeLimit = float(gcfg.get("time_limit_seconds", 30))
    model.Params.MIPGap = float(gcfg.get("mip_gap", 0.0))
    model.Params.Threads = int(gcfg.get("threads", 1))
    model.optimize()

    assert model.Status == gp.GRB.OPTIMAL, (
        f"{evrp_instance}: status={model.Status}, "
        f"runtime={model.Runtime:.3f}s, solcount={model.SolCount}"
    )
    assert model.SolCount >= 1
    assert model.ObjVal >= 0
    assert variables["x"]
