import tempfile
from pathlib import Path

import pytest
import gurobipy as gp


@pytest.mark.advanced
def test_counts_and_parameters(solver_env):
    m = gp.Model("advanced_counts", env=solver_env)
    try:
        m.Params.OutputFlag = 0
        m.Params.Threads = 1

        x = m.addVars(3, lb=0, ub=10)
        m.addConstr(x[0] + x[1] + x[2] <= 10)
        m.setObjective(2 * x[0] + x[1] + x[2], gp.GRB.MAXIMIZE)

        # Gurobi model modifications are lazy; update before querying counts.
        m.update()

        assert m.NumVars == 3
        assert m.NumConstrs == 1

        m.optimize()
        assert m.Status == gp.GRB.OPTIMAL
        assert abs(m.ObjVal - 20.0) < 1e-8
    finally:
        m.dispose()


@pytest.mark.advanced
def test_indicator_constraint(solver_env):
    m = gp.Model("indicator", env=solver_env)
    try:
        b = m.addVar(vtype=gp.GRB.BINARY)
        x = m.addVar(lb=0, ub=10)

        # If b = 1, enforce x >= 5.
        m.addGenConstrIndicator(b, True, x >= 5)
        m.setObjective(x + b, gp.GRB.MAXIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert x.X >= 5 - 1e-7
        assert b.X > 0.5
    finally:
        m.dispose()


@pytest.mark.advanced
def test_solution_pool(solver_env):
    m = gp.Model("solution_pool", env=solver_env)
    try:
        x = m.addVars(3, vtype=gp.GRB.BINARY)
        m.addConstr(gp.quicksum(x[i] for i in range(3)) == 1)
        m.setObjective(gp.quicksum((i + 1) * x[i] for i in range(3)), gp.GRB.MINIMIZE)

        m.Params.PoolSearchMode = 2
        m.Params.PoolSolutions = 3
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert m.SolCount >= 1
    finally:
        m.dispose()


@pytest.mark.advanced
def test_iis_on_infeasible_model(solver_env):
    m = gp.Model("iis", env=solver_env)
    try:
        x = m.addVar(lb=0)
        c1 = m.addConstr(x >= 10, name="lower")
        c2 = m.addConstr(x <= 5, name="upper")
        m.optimize()

        assert m.Status == gp.GRB.INFEASIBLE

        m.computeIIS()
        assert c1.IISConstr == 1
        assert c2.IISConstr == 1
    finally:
        m.dispose()


@pytest.mark.advanced
def test_model_write_and_read(solver_env):
    m = gp.Model("roundtrip", env=solver_env)
    tmp = Path(tempfile.gettempdir()) / "gurobi_ci_roundtrip.lp"
    try:
        x = m.addVar(lb=0, ub=10)
        m.setObjective(x, gp.GRB.MAXIMIZE)
        m.optimize()
        assert m.Status == gp.GRB.OPTIMAL

        m.write(str(tmp))
        assert tmp.exists()

        loaded = gp.read(str(tmp), env=solver_env)
        try:
            loaded.optimize()
            assert loaded.Status == gp.GRB.OPTIMAL
            assert abs(loaded.ObjVal - 10.0) < 1e-8
        finally:
            loaded.dispose()
    finally:
        m.dispose()
        tmp.unlink(missing_ok=True)
