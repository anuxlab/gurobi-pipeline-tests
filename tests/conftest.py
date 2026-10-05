from __future__ import annotations

import os
import pytest

from gurobi_tests.gurobi_env import credentials_from_env


@pytest.fixture(scope="session", autouse=True)
def require_wls_credentials():
    """Fail early with a useful message instead of cryptic KeyError/ValueError."""
    credentials_from_env()


@pytest.fixture
def solver_env():
    """Create and always close one WLS environment per test."""
    from gurobi_tests.gurobi_env import new_env

    env = new_env()
    try:
        yield env
    finally:
        env.dispose()


@pytest.fixture
def evrp_instance():
    return os.getenv("EVRP_INSTANCE", "tiny_evrp.json")
