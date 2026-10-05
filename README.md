# Gurobi Pipeline Tests v2

A small, deterministic Gurobi regression suite for local development and GitHub Actions CI/CD using an Academic WLS license.

## What v2 fixes

The first version had two important reliability problems:

1. The EVRP battery/depot formulation could make otherwise valid routes infeasible because the depot's start-energy state was reused for the return arc.
2. The GitHub matrix could launch many WLS sessions simultaneously. Academic WLS licenses can have a concurrent-session baseline, so an aggressive matrix can fail even when the credentials are correct.

v2 therefore:

- separates static validation from solver tests;
- uses a matrix for clear per-suite/per-instance jobs;
- serializes Gurobi jobs with `max-parallel: 1` by default;
- creates and disposes one Gurobi environment per test;
- validates WLS secrets before running models;
- uploads JUnit XML results even when a test fails;
- uses deterministic LP/MIP/QP/advanced regression cases;
- validates all six research EVRP instances before solving;
- keeps WLS credentials exclusively in GitHub Actions Secrets.

Gurobi's current WLS guidance supports providing `WLSACCESSID`, `WLSSECRET`, and numeric `LICENSEID` through the Python API or a `gurobi.lic` file. WLS requires the client to communicate with Gurobi's servers over the internet. citeturn0search1turn0search4

## Repository

```text
.
├── .github/workflows/gurobi.yaml
├── config/
│   ├── development.yaml
│   └── research.yaml
├── gurobi_tests/
│   ├── config.py
│   ├── evrp_model.py
│   └── gurobi_env.py
├── instances/
│   ├── tiny_evrp.json
│   ├── TS1.json
│   ├── TS2.json
│   ├── TS3.json
│   ├── TS4.json
│   ├── TS5.json
│   └── TS6.json
├── tests/
│   ├── conftest.py
│   ├── test_advanced.py
│   ├── test_evrp.py
│   ├── test_gurobi.py
│   ├── test_lp.py
│   ├── test_mip.py
│   └── test_qp.py
├── pytest.ini
└── requirements.txt
```

## GitHub Secrets

Create these repository secrets:

```text
GRB_WLSACCESSID
GRB_WLSSECRET
GRB_LICENSEID
```

Do not commit `gurobi.lic`, WLS secrets, or API keys. Gurobi explicitly treats the WLS secret as private credential material. citeturn0search1

## Local run

Set the same environment variables in your shell:

```bash
export GRB_WLSACCESSID='...'
export GRB_WLSSECRET='...'
export GRB_LICENSEID='2871490'

python3 -m pip install -r requirements.txt
pytest -v
```

For one EVRP instance:

```bash
export EVRP_INSTANCE=TS1.json
pytest -v tests/test_evrp.py
```

For the research configuration:

```bash
export GUROBI_CONFIG=config/research.yaml
```

The tests use a context-managed/lifecycle-safe Gurobi environment pattern and explicitly dispose the environment after each test. This matters for WLS because an active environment holds a WLS token until the environment is closed and the token lifetime expires. citeturn0search9

## GitHub Actions matrix

The solver job is a matrix with these entries:

```text
smoke
lp
mip
qp
advanced
evrp / tiny_evrp.json
evrp / TS1.json
...
evrp / TS6.json
```

GitHub Actions creates a separate job for every matrix combination. citeturn0search5

The matrix is deliberately set to:

```yaml
max-parallel: 1
```

for Academic WLS reliability. If your WLS license permits multiple concurrent sessions, this can be raised, for example to `2` or `4`.

## Test layers

### Smoke

- Python/gurobipy version
- WLS credential format
- actual WLS environment startup
- one optimization

### LP

- optimal LP
- unbounded LP status

### MIP

- binary knapsack
- assignment model
- integer variable model
- infeasible model detection

### QP

- convex quadratic program
- equality-constrained QP

### Advanced

- parameter round-trip
- solution pool
- model counts
- LP file writing

### EVRP

Each instance checks:

1. JSON/schema validity
2. depot/customer consistency
3. capacity feasibility
4. model construction
5. Gurobi optimization
6. optimal status
7. existence of a solution
8. non-negative objective

The EVRP model is intentionally a CI-sized EVRP-style MILP, not a replacement for your full thesis formulation. It is designed to catch regressions in model construction and solver connectivity.

## Extending this for the thesis

The next research layer should add a separate benchmark workflow rather than making the CI smoke suite responsible for long experiments:

```text
CI regression
    └── fast deterministic tests

Research benchmark
    ├── TS1 ... TS6
    ├── Gurobi/NIP/BPC/ALNS/LLP
    ├── runtime
    ├── objective/profit
    ├── MIP gap
    ├── nodes
    └── CSV + plots
```

That keeps pull requests fast while allowing longer reproducible experiments on demand.
