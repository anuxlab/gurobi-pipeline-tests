from __future__ import annotations

import pytest

from gurobi_tests.config import instance_path
from gurobi_tests.gurobi_env import new_env


@pytest.fixture(scope="session")
def solver_env():
    # ONE Gurobi environment for the whole pytest process.
    # This is deliberate for WLS: Academic WLS has a baseline of two
    # concurrent sessions, and a token can remain counted until expiry.
    env = new_env()
    try:
        env.start()
        yield env
    finally:
        env.dispose()


@pytest.fixture
def evrp_path(request):
    return instance_path(request.param)
