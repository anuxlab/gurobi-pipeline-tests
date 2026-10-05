import os
import pytest
from gurobi_tests.gurobi_env import new_env, credentials_from_env

@pytest.fixture
def solver_env():
    env = new_env()
    try:
        yield env
    finally:
        env.dispose()

@pytest.fixture
def evrp_instance():
    return os.environ.get("EVRP_INSTANCE", "tiny_evrp.json")
