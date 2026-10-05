# Gurobi Pipeline Tests v3

This version is intentionally designed around **Academic WLS session behavior**.

## Why v3 uses one solver job

An Academic WLS license has a baseline of two concurrent Gurobi sessions. A WLS token remains counted until the environment is closed and the token lifespan has expired. Therefore, a GitHub Actions job matrix can unexpectedly accumulate sessions even when each matrix has `max-parallel: 1`.

v3 uses:
- one static validation job (no Gurobi)
- one solver job
- one session-scoped `gurobipy.Env`
- one pytest process
- pytest parameterization as the test matrix
- workflow-level concurrency to prevent overlapping runs

This is more reliable for an academic WLS license.

## Test coverage

### Smoke
- Gurobi version
- WLS environment starts
- tiny optimization

### LP
- optimal LP
- unbounded LP

### MIP
- binary knapsack
- integer model
- assignment model
- infeasible model

### QP
- convex QP
- quadratic objective with equality constraint

### Advanced
- parameter/count verification
- indicator constraint
- solution pool
- IIS computation
- LP write/read round trip

### EVRP
- JSON schema validation
- tiny + TS1-TS6 routing MILP smoke/regression
- capacity constraints
- MTZ subtour elimination
- simple route energy budget

The EVRP files are synthetic CI test instances, not the original benchmark instances from a paper.

## Validation

The package can be statically checked without a Gurobi license, but actual solver/WLS tests must be run on a machine/CI runner with valid Gurobi access.

## Local use

With a downloaded WLS `gurobi.lic` in `~/gurobi.lic`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -v
```

Alternatively, use WLS environment variables:

```bash
export GRB_WLSACCESSID="..."
export GRB_WLSSECRET="..."
export GRB_LICENSEID="2871490"
pytest -v
```

Never commit credentials or `gurobi.lic`.

## GitHub Secrets

Set:
- `GRB_WLSACCESSID`
- `GRB_WLSSECRET`
- `GRB_LICENSEID`

## CI matrix

The test matrix is implemented by pytest parameterization so that all cases share one long-lived WLS environment.

This intentionally avoids an Actions job matrix for solver calls. It is still a matrix of independent test cases, but it does not create multiple cloud machines/sessions.

## Research usage

Keep expensive TS1-TS6 thesis experiments in a separate workflow. These CI instances are deliberately small and deterministic.
