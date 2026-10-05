import pytest
import gurobipy as gp


@pytest.mark.qp
def test_convex_qp(solver_env):
    m = gp.Model("convex_qp", env=solver_env)
    try:
        x = m.addVars(2, lb=-10, ub=10)
        m.addConstr(x[0] + x[1] >= 1)
        m.setObjective(x[0] * x[0] + x[1] * x[1], gp.GRB.MINIMIZE)
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(m.ObjVal - 0.5) < 1e-6
        assert abs(x[0].X - 0.5) < 1e-6
        assert abs(x[1].X - 0.5) < 1e-6
    finally:
        m.dispose()


@pytest.mark.qp
def test_quadratic_objective_with_fixed_sum(solver_env):
    m = gp.Model("qp_fixed_sum", env=solver_env)
    try:
        x = m.addVars(2, lb=0, ub=10)
        m.addConstr(x[0] + x[1] == 4)
        m.setObjective(
            (x[0] - 1) * (x[0] - 1) + (x[1] - 3) * (x[1] - 3),
            gp.GRB.MINIMIZE,
        )
        m.optimize()

        assert m.Status == gp.GRB.OPTIMAL
        assert abs(x[0].X - 1.0) < 1e-6
        assert abs(x[1].X - 3.0) < 1e-6
        assert abs(m.ObjVal) < 1e-7
    finally:
        m.dispose()
