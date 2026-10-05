# Gurobi CI/CD Pipeline Tests

A small, research-oriented CI test harness for Gurobi + `gurobipy` using GitHub Actions and WLS.

## What it tests

- Gurobi Python installation/version
- WLS credential presence and license connectivity
- LP optimization
- MILP optimization
- convex QP optimization
- EVRP-style MILP model on six small research instances
- matrix execution of independent test suites

The EVRP cases are deliberately small so CI remains fast. They are **solver/integration regression instances**, not replacements for full-scale thesis benchmarks.

## Repository layout

```text
.
├── .github/workflows/gurobi.yaml
├── config/
│   ├── development.yaml
│   └── research.yaml
├── instances/
│   ├── tiny_evrp.json
│   ├── TS1.json
│   ├── TS2.json
│   ├── TS3.json
│   ├── TS4.json
│   ├── TS5.json
│   └── TS6.json
├── gurobi_tests/
│   ├── __init__.py
│   ├── config.py
│   ├── gurobi_env.py
│   └── evrp_model.py
├── tests/
│   ├── test_gurobi.py
│   ├── test_lp.py
│   ├── test_mip.py
│   ├── test_qp.py
│   └── test_evrp.py
├── pytest.ini
└── requirements.txt
```

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GRB_WLSACCESSID="..."
export GRB_WLSSECRET="..."
export GRB_LICENSEID="2871490"

pytest -v
pytest -v tests/test_gurobi.py
pytest -v tests/test_lp.py
pytest -v tests/test_mip.py
pytest -v tests/test_qp.py
pytest -v tests/test_evrp.py
```

If you already have a WLS `gurobi.lic`, you can instead point Gurobi at it:

```bash
export GRB_LICENSE_FILE="$HOME/Downloads/gurobi.lic"
```

Do not commit `gurobi.lic` or WLS secrets.

## GitHub Actions secrets

Create these repository secrets:

- `GRB_WLSACCESSID`
- `GRB_WLSSECRET`
- `GRB_LICENSEID`

The workflow passes them to the runner as environment variables.

## Matrix

The workflow runs these suites independently:

- `gurobi`
- `lp`
- `mip`
- `qp`
- `evrp`

For the EVRP suite, the second matrix dimension runs TS1-TS6 independently.

This makes failures easy to identify and allows GitHub Actions to run independent tests in parallel.

## Important WLS point

The GitHub-hosted runner does not need to be on the IIIT Guwahati network after you have generated the academic WLS credentials. WLS requires the runner to reach Gurobi's licensing service over the Internet. Keep the credentials private.

## Recommended workflow

Use the matrix workflow as a **solver integration/regression gate**. Keep expensive full research experiments outside ordinary PR CI, for example as a manually dispatched workflow or a separate benchmark workflow.
