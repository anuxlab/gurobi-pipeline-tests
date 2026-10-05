import json
from pathlib import Path
import gurobipy as gp

def load_instance(name):
    p=Path("instances")/name
    assert p.exists(), f"Missing instance: {p}"
    data=json.loads(p.read_text())
    assert data["depot"] in data["nodes"]
    assert data["customers"]
    for c in data["customers"]:
        assert c in data["nodes"]
    return data

def test_evrp_instance_schema(evrp_instance):
    load_instance(evrp_instance)

def test_evrp_model_builds_and_solves(evrp_instance, solver_env):
    d=load_instance(evrp_instance)
    customers=d["customers"]
    n=len(customers)
    m=gp.Model("evrp_regression", env=solver_env)
    x=m.addVars(n, vtype=gp.GRB.BINARY, name="serve")
    m.addConstr(gp.quicksum(x[i] for i in range(n)) >= 1)
    m.setObjective(gp.quicksum(float(d["nodes"][c].get("reward",1.0))*x[i] for i,c in enumerate(customers)), gp.GRB.MAXIMIZE)
    m.optimize()
    assert m.Status == gp.GRB.OPTIMAL
    assert m.SolCount > 0
    m.dispose()
