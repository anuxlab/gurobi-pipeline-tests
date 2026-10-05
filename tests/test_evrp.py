import json

import pytest

from gurobi_tests.config import configured_instances, instance_path
from gurobi_tests.evrp_model import build_routing_model, load_instance, validate_instance


ALL_INSTANCES = configured_instances()


@pytest.mark.evrp
@pytest.mark.parametrize("instance_name", ALL_INSTANCES, ids=ALL_INSTANCES)
def test_instance_schema(instance_name):
    path = instance_path(instance_name)
    assert path.exists(), f"Missing instance: {path}"

    data = load_instance(path)
    validate_instance(data)


@pytest.mark.evrp
@pytest.mark.parametrize("instance_name", ALL_INSTANCES, ids=ALL_INSTANCES)
def test_evrp_model_solves(instance_name, solver_env):
    data = load_instance(instance_path(instance_name))

    model, variables = build_routing_model(solver_env, data)
    try:
        model.Params.TimeLimit = 30
        model.Params.MIPGap = 0.0
        model.optimize()

        assert model.Status == 2, (
            f"{instance_name}: expected OPTIMAL, got status {model.Status}"
        )
        assert model.SolCount > 0
        assert model.ObjVal >= 0
    finally:
        model.dispose()
