import os
import gurobipy as gp


def test_gurobi_wls():
    env = gp.Env(params={
        "WLSACCESSID": os.environ["GRB_WLSACCESSID"],
        "WLSSECRET": os.environ["GRB_WLSSECRET"],
        "LICENSEID": int(os.environ["GRB_LICENSEID"]),
    })

    model = gp.Model("ci_test", env=env)

    x = model.addVar(lb=0, name="x")
    y = model.addVar(lb=0, name="y")

    model.addConstr(x + y <= 10)
    model.setObjective(x + 2 * y, gp.GRB.MAXIMIZE)

    model.optimize()

    assert model.Status == gp.GRB.OPTIMAL
    assert abs(model.ObjVal - 20.0) < 1e-6

    env.close()